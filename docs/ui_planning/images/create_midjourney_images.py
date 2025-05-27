import os
import requests
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
DISCORD_USER_TOKEN = os.getenv('DISCORD_USER_TOKEN')

# Load prompts and filenames from YAML file
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
    filename = item['filename']
    response = submit_prompt(prompt)
    print(f"Prompt submitted: {prompt}")
