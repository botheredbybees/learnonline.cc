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
