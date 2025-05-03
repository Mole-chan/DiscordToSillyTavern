A simple conversion tool to convert chat history from both Discord-based and Janitor AI chatbots to SillyTavern compliant JSONL logs.

REQUIREMENTS

Before running this script, please run the command "pip install -r requirements.txt" to automatically install any dependencies.

-----

CONVERT FROM DISCORD

Gather chat history from Discord using DiscordChatExporter(https://github.com/Tyrrrz/DiscordChatExporter). Export the history in JSON format. You may need to change the file extension to JSON.
Open the terminal/command prompt and convert the JSON file with this command:

python sillytavern_chat_converter.py <PATH_TO_INPUT>.json <PATH_TO_OUTPUT>.jsonl --user_name <YOUR_USERNAME> (optional)

The script will try to detect the first non-bot response and draw your username from it. However, if it cannot determine which participant is a bot, it will ask for your username.

-----

CONVERT FROM JANITOR

**METHOD 1 (LEGACY, NOT RECOMMENDED)**
Install the Instant Data Scraper for Chrome (https://chromewebstore.google.com/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah).
Open the desired chat and scroll up to the first post. Launch Instant Data Scraper, check "Infinite Scroll" and click "Start Crawling". 
You may have to manually select a post to point the scraper in the right direction.
Once everything is scraped, download as CSV.
Open the CSV and delete the columns "chakra-image src" and "chakra-image src 2". Rename the name column to "name". Rename the message columns "mes-1", "mes-2", "mes-3", etc.

Open the terminal/command prompt and convert the CSV file with this command:

python sillytavern_chat_converter.py <PATH_TO_INPUT>.csv <PATH_TO_OUTPUT>.jsonl --user_name <YOUR_USERNAME> (optional)

This method is old and unreliable. If you choose to use it, I will not assist in data scraping or promise consistent results. 
It is only recommended if you already have chatlogs in this format.

**METHOD 2**
Install JanitorAI Chat Downloader for Chrome (https://chromewebstore.google.com/detail/janitorai-chat-downloader/agcmemnhmffojajaaoloemjndnbijmam) and follow their instructions to download your chat history.
Open the terminal/command prompt and convert the JSON file with this command:

python sillytavern_chat_converter.py <PATH_TO_INPUT>.json <PATH_TO_OUTPUT>.jsonl --user_name <YOUR_USERNAME> (REQUIRED)

**METHOD 3** 
Just use JanitorAI Chat Downloader's "Export as > SillyTavern Chat" function. The conversion method for this utility had already been written before I realized this exists.
The output quality for both is similar, but JACD is faster.



Happy Chatting!
