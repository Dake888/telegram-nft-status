# telegram-nft-status
A simple bot to track the amount of NFTs of your project for active member of telegram chat and display this amount in the members's title without any administrator rights.

_**The bot is useful for those who want to decorate the chat of their project, as well as increase the engagement of the audience. Use this bot in combination with other bots to create the best user experience!**_

## Quick start

Before you start working with the bot, you should make sure that all modules from **requirements.txt** installed in your environment.
An easy way to quickly install all requirements: `pip install -r /path/to/requirements.txt`

You will also need to fill out a **secretData.py** with your token data anc telegram chat ID.
```
tonapi_token = ''
bot_token = ''
chat_id = ''
```

### Configure your parameters in the config.py:
1. **Fill in the link to connect to your database in database_url variable.** In this database, create a table named verify, which should store the data of your NFT owners in two fields: tgid (int) - the user's unique telegram id and owner (string) - the user's address in the blockchain (any version).
2. **Fill in the collection variable that points to your NFT collection.** The address can be represented in any blockchain format.
3. **Fill in how the name of your NFT will be displayed in singular and plural in the nft_name variable.** For example, "number" for a collection of Anonymous Telegram Numbers. The code itself will determine in which of the cases it needs to put the plural in the title.
4. **Select which events will be a trigger for the bot to consider the chat member as active and update the title of the chat member in allowed_updates list (optional).** In the current interpretation, the bot considers as active those participants who write new messages or update messages. For more information about telegram events that are cached by the bot, follow the link - https://core.telegram.org/bots/api#getupdate.
5. **Fill in the telegram id of the chat members for whom you do not want to set or change the title in exc_ids variable (optional).** It can be useful if admins have different titles in your chat. Bots are not required.

The bot will add titles to active members until their number (the number of administrators in the group) exceeds 50. Then, the bot will remove the title from those who have been active most recently and add the title to those who have been active recently, but not has title, excluding members from exc_ids.

You can change how often the bot starts by changing the parameter on line 60 in main.py
