
# MidJourney and Discord Integration Setup

This guide will walk you through setting up and using the MidJourney and Discord integration scripts to automate image generation and downloading using MidJourney prompts.

## Prerequisites

- A Discord account
- A MidJourney subscription (Pro or higher recommended)
- Python 3.x installed on your system
- Required Python packages: `discord.py`, `python-dotenv`, `requests`, `pyyaml`

## Step 1: Create a Discord Bot

1. **Go to the Discord Developer Portal**
   - Visit: [https://discord.com/developers/applications](https://discord.com/developers/applications)
   - Log in with your Discord account.

2. **Create a New Application**
   - Click the **“New Application”** button.
   - Name it something like `MidJourney Listener Bot`.
   - Click **“Create”**.

3. **Create a Bot User**
   - In the left sidebar, click **“Bot”**.
   - Click **“Add Bot”** → Confirm with **“Yes, do it!”**
   - You now have a bot user!

4. **Copy the Bot Token**
   - Under the **Bot** section, click **“Reset Token”** (if needed), then **“Copy”**.
   - **Save this token securely** — you’ll use it in your Python script (in your `.env` file).

5. **Enable Privileged Intents**
   - Still in the **Bot** section:
     - Scroll down to **Privileged Gateway Intents**
     - Enable:
       - ✅ **Message Content Intent**
       - ✅ **Server Members Intent** (optional, but safe to enable)

6. **Invite the Bot to Your Server**
   - Go to the **OAuth2 → URL Generator** section.
   - Under **Scopes**, check:
     - ✅ `bot`
   - Under **Bot Permissions**, check:
     - ✅ `Read Messages/View Channels`
     - ✅ `Send Messages`
     - ✅ `Read Message History`
     - ✅ `Attach Files` (optional, for future features)
   - Copy the generated URL at the bottom.
   - Paste it into your browser and **invite the bot** to your server.

## Step 2: Configure Environment Variables

Create a `.env` file in the same directory as your scripts with the following content:

DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CHANNEL_ID=your_channel_id_here

Replace `your_bot_token_here` with your actual bot token
Replace `your_channel_id_here` with the ID of the channel where MidJourney posts images

## Step 3: Install Required Python Packages

Run the following command to install the necessary packages:

pip install discord.py python-dotenv requests pyyaml

## Step 4: Create the `prompts.yaml` File

Create a file named `prompts.yaml` in the same directory as your scripts with the following content:

prompts:
  - prompt: "Fantasy-style illustrated lore panel for the Merchant Guild"
    filename: merchant_lore_panel.png
  - prompt: "Stylized portrait of a seasoned merchant-scholar"
    filename: merchant_npc_portrait.png
  - prompt: "RPG-style dialogue box for the Merchant Guild"
    filename: merchant_dialogue_box.png

## Step 5: Create the `create_midjourney_images.py` Script

Create a file named `create_midjourney_images.py` with the following content:

import os
import requests
from dotenv import load_dotenv
import yaml

# Load environment variables from .env file
load_dotenv()

DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
DISCORD_USER_TOKEN = os.getenv('DISCORD_USER_TOKEN')
DISCORD_SESSION_ID = os.getenv('DISCORD_SESSION_ID')  # Not used in this basic script

# Load prompts from YAML file
with open('prompts.yaml', 'r') as file:
    prompts_data = yaml.safe_load(file)

# Function to submit a prompt to MidJourney
def submit_prompt(prompt):
    url = f"https://discord.com/api/v9/channels/{DISCORD_CHANNEL_ID}/messages"
    headers = {
        "Authorization": DISCORD_USER_TOKEN,
        "Content-Type": "application/json"
    }
    data = {
        "content": f"/imagine prompt: {prompt}",
        "tts": False
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Failed to submit prompt: {prompt}")
        print(f"Status Code: {response.status_code}, Response: {response.text}")
    return response.json()

# Submit prompts from YAML file
for item in prompts_data['prompts']:
    prompt = item['prompt']
    response = submit_prompt(prompt)
    print(f"Prompt submitted: {prompt}")

## Step 6: Create the `get_midjourney_images.py` Script

Create a file named `get_midjourney_images.py` with the following content:

import os
import yaml
import discord
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

# Create a directory to save images if it doesn't exist
SAVE_DIR = 'midjourney_images'
os.makedirs(SAVE_DIR, exist_ok=True)

# Load prompts and filenames from YAML file
with open('prompts.yaml', 'r') as file:
    prompts_data = yaml.safe_load(file)

# Initialize the Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Function to match prompt to filename
def get_filename_from_prompt(prompt):
    for item in prompts_data['prompts']:
        if item['prompt'] in prompt:
            return item['filename']
    return None

@client.event
async def on_ready():
    print(f'Bot is ready. Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.channel.id == DISCORD_CHANNEL_ID:
        if message.author.bot and 'MidJourney Bot' in message.author.name:
            if message.attachments:
                for attachment in message.attachments:
                    image_url = attachment.url
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        prompt = message.content
                        filename = get_filename_from_prompt(prompt)
                        if filename:
                            guild_name = filename.split('_')[0]
                            guild_dir = os.path.join(SAVE_DIR, guild_name)
                            os.makedirs(guild_dir, exist_ok=True)
                            file_path = os.path.join(guild_dir, filename)
                            with open(file_path, 'wb') as file:
                                file.write(response.content)
                            print(f'Downloaded and saved image: {file_path}')
                        else:
                            print(f'No matching filename found for prompt: {prompt}')
                    else:
                        print(f'Failed to download image from {image_url}')

client.run(DISCORD_BOT_TOKEN)

## Step 7: Run the Scripts

1. Run the `create_midjourney_images.py` script to submit prompts to MidJourney.
2. Run the `get_midjourney_images.py` script to listen for image responses and download them.

