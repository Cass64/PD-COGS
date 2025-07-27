import discord
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()
token = os.getenv('ETHERYA')

# Initialiser le client Discord avec les intents
intents = discord.Intents.default()
intents.members = True  # Assurez-vous d'activer les intents nécessaires
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot connecté en tant que {client.user}')

# Démarrer le bot
client.run(token)
