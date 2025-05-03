
import pandas as pd
import json
from datetime import datetime, timedelta
import argparse
import os

def format_datetime_portable(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%B %-d, %Y %-I:%M%p").lower()
    except:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).strftime("%B %#d, %Y %#I:%M%p").lower()

def convert_csv_to_jsonl(csv_path, user_name, start_time_str="2025-05-01 20:00", interval_minutes=3):
    df = pd.read_csv(csv_path)
    mes_columns = [col for col in df.columns if col.startswith("mes")]
    df["mes"] = df[mes_columns].fillna("").agg("\n".join, axis=1).str.strip()
    df = df[df["mes"] != ""].reset_index(drop=True)

    start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
    df["send_date"] = [format_datetime_portable(start_time + timedelta(minutes=i * interval_minutes)) for i in range(len(df))]

    inferred_user = df.loc[1, "name"] if user_name is None else user_name
    print(f"[CSV] Using user name: {inferred_user}")

    def transform_row(row):
        is_user = (row["name"] == inferred_user)
        record = {
            "name": row["name"],
            "is_user": is_user,
            "is_system": False,
            "send_date": row["send_date"],
            "mes": row["mes"],
            "extra": {} if not is_user else {"isSmallSys": False}
        }
        if is_user:
            record["force_avatar"] = "User Avatars/user-default.png"
        return record

    return [transform_row(row) for _, row in df.iterrows()]

def convert_discord_json_to_jsonl(json_data, user_name=None):
    messages = json_data.get("messages", [])
    if not messages:
        raise ValueError("No messages found in JSON.")

    inferred_user = None
    for msg in messages:
        if not msg.get("author", {}).get("isBot", False):
            inferred_user = msg["author"]["nickname"]
            break

    if not any(msg.get("author", {}).get("isBot", False) for msg in messages):
        if user_name is None:
            raise ValueError("No bot messages found and no fallback user_name provided.")
        inferred_user = user_name
    else:
        inferred_user = inferred_user or user_name

    print(f"[Discord] Inferred user name: {inferred_user}")

    results = []
    for msg in messages:
        nickname = msg.get("author", {}).get("nickname", "Unknown")
        is_user = (nickname == inferred_user)
        try:
            dt = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
            send_date = format_datetime_portable(dt)
        except Exception:
            send_date = "unknown"

        entry = {
            "name": nickname,
            "is_user": is_user,
            "is_system": False,
            "send_date": send_date,
            "mes": msg.get("content", ""),
            "extra": {} if not is_user else {"isSmallSys": False}
        }
        if is_user:
            entry["force_avatar"] = "User Avatars/user-default.png"
        results.append(entry)

    return results

def convert_janitor_json_to_jsonl(json_data, user_name):
    if not user_name:
        raise ValueError("For Janitor JSON, --user_name must be provided.")

    character_name = json_data["character"]["name"]
    messages = json_data["chatMessages"][::-1]

    print(f"[Janitor] Detected character: {character_name}")

    def transform_message(msg):
        name = character_name if msg.get("is_bot", False) else user_name
        is_user = not msg.get("is_bot", False)
        send_date = format_datetime_portable(msg["created_at"])

        record = {
            "name": name,
            "is_user": is_user,
            "is_system": False,
            "send_date": send_date,
            "mes": msg["message"],
            "extra": {} if not is_user else {"isSmallSys": False}
        }
        if is_user:
            record["force_avatar"] = "User Avatars/user-default.png"
        return record

    return [transform_message(msg) for msg in messages]

def strict_order(record):
    keys_order = ["name", "is_user", "is_system", "send_date", "mes", "extra", "force_avatar"]
    return {k: record[k] for k in keys_order if k in record}

def save_as_jsonl(records, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for item in records:
            f.write(json.dumps(strict_order(item)) + "\n")
    print(f"Exported SillyTavern JSONL to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert CSV, Discord JSON, or Janitor JSON to SillyTavern JSONL format.")
    parser.add_argument("input_path", help="Path to the input file (CSV or JSON).")
    parser.add_argument("output_path", help="Path to save the output JSONL file.")
    parser.add_argument("--user_name", help="Required for Janitor JSON. Optional fallback for others.")
    parser.add_argument("--start_time", default="2025-05-01 20:00", help="Start datetime for CSV (default: 2025-05-01 20:00)")
    parser.add_argument("--interval", type=int, default=3, help="Minutes between messages for CSV (default: 3)")

    args = parser.parse_args()
    ext = os.path.splitext(args.input_path)[1].lower()

    if ext == ".csv":
        records = convert_csv_to_jsonl(args.input_path, args.user_name, args.start_time, args.interval)
    elif ext == ".json":
        with open(args.input_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        is_janitor = "chatMessages" in json_data and "character" in json_data
        if is_janitor:
            records = convert_janitor_json_to_jsonl(json_data, args.user_name)
        else:
            records = convert_discord_json_to_jsonl(json_data, args.user_name)
    else:
        raise ValueError("Unsupported file type. Only .csv and .json are supported.")

    save_as_jsonl(records, args.output_path)
