# PteroBot Documentation
Welcome to the official documentation for PteroBot - Your Discord bot for seamless interaction with the Pterodactyl game panel!

# Full and more comprehensive documentation available here https://wiki.codeprobe.xyz/e/en/PteroBot

## Introduction
PteroBot is a powerful Discord bot designed to simplify server management on the Pterodactyl game panel. Whether you're a server administrator or a gamer looking for a convenient way to monitor and control your servers, PteroBot has you covered.

### Features
- **Server Control**: Start, stop, restart, and kill servers effortlessly using Discord commands!
<details>
  <summary>Example</summary>
  <img src="/discord_gdjx1p4ecv.gif" alt="Start Server GIF" onclick="toggleGif(this)">
</details>

- **Status Check**: Instantly check the online or offline status of your servers.
<details>
  <summary>Example</summary>
  <img src="/0f749e55-514f-4275-b9c4-4f43bbefdbd5.gif" alt="Start Server GIF" onclick="toggleGif(this)">
</details>

- **Logs and Performance:** Access server logs and monitor performance and resource usage in real time!
<details>
  <summary>Example</summary>
  <img src="/discord_nyokqq11yc.gif" alt="Start Server GIF" onclick="toggleGif(this)">
</details>

- **Toggle:** Enable / Disable the bot with a custom message! 
> Only the owner of the bot can Enable/Disable the bot!
{.is-warning}
<details>
  <summary>Example</summary>
  <img src="/discord_ddlizzbcsq.gif" alt="Start Server GIF" onclick="toggleGif(this)">
</details>

> In the current version 4.1, the bot doesn't have permission management, so anyone can use the commands appart from the /toggle command, I am actively working to implement role permissions!
{.is-info}

## Getting Started

To begin using PteroBot, follow these steps:

### 1. Create a Bot App on Discord Developer Portal

- Visit the [Discord Developer Portal](https://discord.com/developers/applications).
- Click on "New Application" and give your bot a name.
- Navigate to the "Bot" tab and click "Add Bot."
- Under the "TOKEN" section, click "Copy" to copy your bot token.

### 2. Save Bot Token in `token.json`

- In the main directory of your PteroBot script, create a file named `token.json`.
- Open `token.json` in a text editor and paste the bot token:

```json
{
  "token": "YOUR_BOT_TOKEN_HERE"
}
```
- *Replace YOUR_BOT_TOKEN_HERE with the actual bot token you copied.*

> This step is out of order, you can come back to it after step 4. 
You can just edit the config.json that is provided on my github page!
{.is-warning}


### 3. Invite PteroBot or Custom name to Your Discord Server

- Go back to the Discord Developer Portal and select the "OAuth2" tab.
- In the "OAuth2 URL Generator" section, check the "bot" scope.
- Below, select the required bot permissions based on your preferences.
- Copy the generated URL and open it in a new browser tab.
- Choose the server where you want to invite PteroBot and click "Authorize."

### 4. Set Up PteroBot on the Pterodactyl Panel

Now that your bot is on Discord, let's integrate it with the Pterodactyl panel:

#### a. Download the Generic Python Egg

- Download the generic Python egg from [this GitHub repository](https://github.com/parkervcp/eggs/tree/master/generic/python).

#### b. Add the Egg to Pterodactyl Panel

- Follow the instructions on the [GitHub repository](https://github.com/parkervcp/eggs/tree/master/generic/python) to add the downloaded egg to the Pterodactyl panel using the provided JSON file.

#### c. Upload Files to Pterodactyl Panel

- Download the necessary files (`app.py`, `requirements.txt`, and `token.json`) from [my GitHub repository](https://github.com/Tumba123/pterobot).
- Upload these files to your Pterodactyl panel. You can use the Pterodactyl web interface to upload them to your server's main directory.

#### d. Configure PteroBot

- Run the `/setup` command in your Discord server where PteroBot is located.
- Input the Pterodactyl panel URL, panel API key, and your Discord owner ID as prompted.

#### e. Reboot PteroBot

- Reboot PteroBot to apply the new configuration.

> If you want to use custom emojis, you will need to upload them to the server and edit each emoji in the code... In the previews the bot has nice custom emojis but that is not possible unless you join with the bot in my server too. So I removed them.
{.is-warning}

> You could provide me with an invite link in the support server and I will gladly add the bot to my private dev server so that you can enjoy the custom servers but that is on you, how much you trust a stranger not to mess with your stuff.
{.is-warning}





After completing these steps, your PteroBot should be successfully connected to both Discord and the Pterodactyl panel. If you encounter any issues, refer to the [documentation](https://wiki.codeprobe.xyz/en/PteroBot) or join my [Discord server](https://discord.gg/3qwqqA4GKF) for assistance.


