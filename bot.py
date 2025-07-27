import discord
from discord.ext import commands, tasks
from discord import app_commands, Embed, ButtonStyle, ui
from discord.ui import Button, View, Select, Modal, TextInput, button
from discord.ui import Modal, TextInput, Button, View
from discord.utils import get
from discord import TextStyle
from functools import wraps
import os
from discord import app_commands, Interaction, TextChannel, Role
import io
import random
import asyncio
import time
import re
import subprocess
import sys
import math
import traceback
from keep_alive import keep_alive
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
import pymongo
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import psutil
import pytz
import platform
from discord.ui import Select, View
from typing import Optional
from discord import app_commands, Interaction, Embed, SelectOption
from discord.ui import View, Select
import uuid
from zoneinfo import ZoneInfo
# Matplotlib (à mettre AVANT plt)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import matplotlib.ticker as ticker
import numpy as np

# Importation des fonctions utilitaires
from utils import (
    create_embed, has_permission, is_higher_or_equal, send_log, send_dm,
    load_guild_settings, get_premium_servers, is_blacklisted, add_sanction,
    get_log_channel, get_cf_config, get_presentation_channel_id, get_user_partner_info,
    get_protection_data, format_mention, generate_global_status_bar, format_protection_field,
    notify_owner_of_protection_change, is_valid_url, is_admin_or_isey,
    THUMBNAIL_URL, EMOJIS_SERVEURS, ETHERYA_ID, boost_bar, sensitive_categories,
    word_to_category, active_alerts, giveaways, ended_giveaways, fast_giveaways,
    user_cooldown, sniped_messages, stats_collection33
)

token = os.environ['ETHERYA']
VERIFICATION_CODE = os.environ['VERIFICATION_CODE']
intents = discord.Intents.all()
start_time = time.time()
# client = discord.Client(intents=intents) # Remplacé par commands.Bot
status_message = None  # Pour stocker le message envoyé

#Configuration du Bot:
# --- ID Owner Bot ---
ISEY_ID = 792755123587645461
ID_CANAL = 1376899306719547503

# --- ID PROJECT : DELTA SERVER ---
GUILD_ID = 1359963854200639498

# --- ID Staff Serveur Delta ---
PROJECT_DELTA = 1359963854200639498
STAFF_PROJECT = 1359963854422933876
STAFF_DELTA = 1362339333658382488
ALERT_CHANNEL_ID = 1361329246236053586
ALERT_NON_PREM_ID = 1364557116572172288
STAFF_ROLE_ID = 1362339195380568085
CHANNEL_ID = 1375496380499493004

# --- ID Sanctions Serveur Delta ---
WARN_LOG_CHANNEL = 1362435917104681230
UNWARN_LOG_CHANNEL = 1362435929452707910
BLACKLIST_LOG_CHANNEL = 1362435853997314269
UNBLACKLIST_LOG_CHANNEL = 1362435888826814586

# --- ID Gestion Delta ---
SUPPORT_ROLE_ID = 1359963854422933876
SALON_REPORT_ID = 1361362788672344290
ROLE_REPORT_ID = 1362339195380568085
TRANSCRIPT_CHANNEL_ID = 1361669998665535499
STATUT_ID = 1360361796464021745

# --- ID Gestion Clients Delta ---
LOG_CHANNEL_RETIRE_ID = 1360864806957092934
LOG_CHANNEL_ID = 1360864790540582942

# --- ID Etherya ---
AUTORIZED_SERVER_ID = 1034007767050104892

# Connexion MongoDB
mongo_uri = os.getenv("MONGO_DB")  # URI de connexion à MongoDB
print("Mongo URI :", mongo_uri)
client_mongo = MongoClient(mongo_uri) # Renommé pour éviter le conflit avec discord.Client
db = client_mongo['Cass-Eco2']
db2 = client_mongo['DELTA-ECO']

# Collections
collection = db['setup']  # Configuration générale
collection2 = db['setup_premium']  # Serveurs premium
collection3 = db['bounty']  # Primes et récompenses des joueurs
collection4 = db['protection'] #Serveur sous secu ameliorer
collection5 = db ['clients'] #Stock Clients
collection6 = db ['partner'] #Stock Partner
collection7= db ['sanction'] #Stock Sanction
collection8 = db['idees'] #Stock Idées
collection9 = db['stats'] #Stock Salon Stats
collection10 = db['eco'] #Stock Les infos Eco
collection11 = db['eco_daily'] #Stock le temps de daily
collection12 = db['rank'] #Stock les Niveau
collection13 = db['eco_work'] #Stock le temps de Work
collection14 = db['eco_slut'] #Stock le temps de Slut
collection15 = db['eco_crime'] #Stock le temps de Crime
collection16 = db['ticket'] #Stock les Tickets
collection17 = db['team'] #Stock les Teams
collection18 = db['logs'] #Stock les Salons Logs
collection19 = db['wl'] #Stock les whitelist
collection20 = db['suggestions'] #Stock les Salons Suggestion
collection21 = db['presentation'] #Stock les Salon Presentation
collection22 = db['absence'] #Stock les Salon Absence
collection23 = db['back_up'] #Stock les Back-up
collection24 = db['delta_warn'] #Stock les Warn Delta
collection25 = db['delta_bl'] #Stock les Bl Delta
collection26 = db['alerte'] #Stock les Salons Alerte
collection27 = db['guild_troll'] #Stock les serveur ou les commandes troll sont actif ou inactif
collection28 = db['sensible'] #Stock les mots sensibles actif des serveurs
collection31 = db ['delta_event'] #Stock les serveur, avec le nombres de membres et le owner
collection32 = db['delta_statut']
collection33 = db['ds_stats']


# Fonction pour récupérer le préfixe depuis la base de données
async def get_prefix(bot, message):
    if not message.guild:
        return "+" # Préfixe par défaut pour les DMs

    guild_data = collection.find_one({"guild_id": str(message.guild.id)})
    return guild_data['prefix'] if guild_data and 'prefix' in guild_data else '+'

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# Dictionnaire pour stocker les paramètres de chaque serveur
bot.GUILD_SETTINGS = {}

# Passage des collections à l'objet bot pour un accès facile dans les cogs
bot.db_collections = {
    "setup": collection,
    "setup_premium": collection2,
    "bounty": collection3,
    "protection": collection4,
    "clients": collection5,
    "partner": collection6,
    "sanction": collection7,
    "idees": collection8,
    "stats": collection9,
    "eco": collection10,
    "eco_daily": collection11,
    "rank": collection12,
    "eco_work": collection13,
    "eco_slut": collection14,
    "eco_crime": collection15,
    "ticket": collection16,
    "team": collection17,
    "logs": collection18,
    "wl": collection19,
    "suggestions": collection20,
    "presentation": collection21,
    "absence": collection22,
    "back_up": collection23,
    "delta_warn": collection24,
    "delta_bl": collection25,
    "alerte": collection26,
    "guild_troll": collection27,
    "sensible": collection28,
    "delta_event": collection31,
    "delta_statut": collection32,
    "ds_stats": collection33
}

# Passage des IDs importants à l'objet bot
bot.config_ids = {
    "ISEY_ID": ISEY_ID,
    "ID_CANAL": ID_CANAL,
    "GUILD_ID": GUILD_ID,
    "PROJECT_DELTA": PROJECT_DELTA,
    "STAFF_PROJECT": STAFF_PROJECT,
    "STAFF_DELTA": STAFF_DELTA,
    "ALERT_CHANNEL_ID": ALERT_CHANNEL_ID,
    "ALERT_NON_PREM_ID": ALERT_NON_PREM_ID,
    "STAFF_ROLE_ID": STAFF_ROLE_ID,
    "CHANNEL_ID": CHANNEL_ID,
    "WARN_LOG_CHANNEL": WARN_LOG_CHANNEL,
    "UNWARN_LOG_CHANNEL": UNWARN_LOG_CHANNEL,
    "BLACKLIST_LOG_CHANNEL": BLACKLIST_LOG_CHANNEL,
    "UNBLACKLIST_LOG_CHANNEL": UNBLACKLIST_LOG_CHANNEL,
    "SUPPORT_ROLE_ID": SUPPORT_ROLE_ID,
    "SALON_REPORT_ID": SALON_REPORT_ID,
    "ROLE_REPORT_ID": ROLE_REPORT_ID,
    "TRANSCRIPT_CHANNEL_ID": TRANSCRIPT_CHANNEL_ID,
    "STATUT_ID": STATUT_ID,
    "LOG_CHANNEL_RETIRE_ID": LOG_CHANNEL_RETIRE_ID,
    "LOG_CHANNEL_ID": LOG_CHANNEL_ID,
    "AUTORIZED_SERVER_ID": AUTORIZED_SERVER_ID,
    "VERIFICATION_CODE": VERIFICATION_CODE
}

# Compteur de commandes exécutées (exemple simple)
bot.command_count = 0

# Dictionnaire en mémoire pour stocker les paramètres de protection par guild_id
bot.protection_settings = {}
bot.ban_times = {}  # Dictionnaire pour stocker les temps de bans

# Tâche de fond pour mettre à jour les stats toutes les 5 secondes
@tasks.loop(minutes=5)
async def update_stats():
    all_stats = bot.db_collections["stats"].find()

    for data in all_stats:
        guild_id = int(data["guild_id"])
        guild = bot.get_guild(guild_id)
        if not guild:
            continue

        role = guild.get_role(data.get("role_id"))
        member_channel = guild.get_channel(data.get("member_channel_id"))
        role_channel = guild.get_channel(data.get("role_channel_id"))
        bots_channel = guild.get_channel(data.get("bots_channel_id"))

        total_members = guild.member_count
        role_members = len([m for m in guild.members if role in m.roles and not m.bot]) if role else 0
        total_bots = len([m for m in guild.members if m.bot])

        try:
            if member_channel:
                await member_channel.edit(name=f"👥 Membres : {total_members}")
            if role_channel:
                await role_channel.edit(name=f"🎯 {role.name if role else 'Rôle'} : {role_members}")
            if bots_channel:
                await bots_channel.edit(name=f"🤖 Bots : {total_bots}")
        except discord.Forbidden:
            print(f"⛔ Permissions insuffisantes pour modifier les salons dans {guild.name}")
        except Exception as e:
            print(f"⚠️ Erreur lors de la mise à jour des stats : {e}")

@tasks.loop(minutes=5)
async def urgence_ping_loop():
    await bot.wait_until_ready()

    guild = bot.get_guild(bot.config_ids["GUILD_ID"])
    if guild is None:
        print(f"[ERREUR] Impossible de récupérer le serveur avec l'ID {bot.config_ids['GUILD_ID']}")
        return

    channel = guild.get_channel(bot.config_ids["CHANNEL_ID"])
    if channel is None:
        print(f"[ERREUR] Impossible de récupérer le salon avec l'ID {bot.config_ids['CHANNEL_ID']}")
        return

    for user_id, data in list(active_alerts.items()):
        if not data.get("claimed"):
            try:
                await channel.send(f"<@&{bot.config_ids['STAFF_DELTA']}> 🚨 Urgence toujours non claimée.")
            except Exception as e:
                print(f"Erreur lors de l'envoi du message d'urgence : {e}")

@tasks.loop(minutes=5)
async def update_bot_presence():
    guild_count = len(bot.guilds)
    member_count = sum(guild.member_count for guild in bot.guilds)

    activity_types = [
        discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} Membres"),
        discord.Activity(type=discord.ActivityType.streaming, name=f"{guild_count} Serveurs"),
        discord.Activity(type=discord.ActivityType.playing, name="Project : Delta"),
    ]

    status_types = [discord.Status.online, discord.Status.idle, discord.Status.dnd]

    activity = random.choice(activity_types)
    status = random.choice(status_types)

    await bot.change_presence(activity=activity, status=status)

bot.ping_history = []
bot.critical_ping_counter = 0

@tasks.loop(minutes=2)
async def envoyer_ping():
    channel = bot.get_channel(bot.config_ids["ID_CANAL"])
    if channel:
        embed = Embed(
            title="<:dev_white_snoway:1376909968141451274> Project : Delta — Système de Présence Actif",
            description=(
                "<a:actif:1376677757081358427> **Le bot est actuellement en ligne et fonctionne parfaitement.**\n\n"
                "<:Signal_Bar_Green:1376912206427590706> Un signal automatique est émis toutes les **2 minutes** afin d'assurer :\n"
                "<a:fleche3:1376557416216268921> Un *suivi en temps réel* du statut du bot\n"
                "<a:fleche3:1376557416216268921> Une *surveillance continue* de son bon fonctionnement\n\n"
                "<:yao_whitefleche:1376912431573504090> Ce système permet une **réactivité maximale** en cas de panne ou d’interruption."
            ),
            color=0xffffff
        )
        embed.set_footer(text="Système automatique de surveillance — Project : Delta")
        await channel.send(embed=embed)

async def update_status_embed():
    channel = bot.get_channel(bot.config_ids["STATUT_ID"])
    if channel is None:
        print("Salon introuvable.")
        return

    statut_data = bot.db_collections["delta_statut"].find_one({"_id": "statut_embed"})
    message_id = statut_data.get("message_id") if statut_data else None

    total_members = sum(g.member_count for g in bot.guilds)
    uptime = datetime.utcnow() - datetime.utcfromtimestamp(bot.uptime)
    ping = round(bot.latency * 1000)
    total_commands = bot.command_count # Utilise le compteur global du bot

    if ping <= 115:
        status = {
            "emoji": "<a:actif:1376677757081358427>",
            "text": "**Tout fonctionne parfaitement !**",
            "color": discord.Color.green(),
            "graph": "#00FF00",
            "channel_emoji": "🟢"
        }
        bot.critical_ping_counter = 0
    elif ping <= 200:
        status = {
            "emoji": "<a:bof:1376677733710692382>",
            "text": "**Performance moyenne.**",
            "color": discord.Color.orange(),
            "graph": "#FFA500",
            "channel_emoji": "🟠"
        }
        bot.critical_ping_counter = 0
    else:
        status = {
            "emoji": "<a:inactif:1376677787158577242>",
            "text": "**Problème de latence détecté !**",
            "color": discord.Color.red(),
            "graph": "#FF0000",
            "channel_emoji": "🔴"
        }
        bot.critical_ping_counter += 1

    alert_triggered = bot.critical_ping_counter >= 3

    bot.ping_history.append(ping)
    if len(bot.ping_history) > 10:
        bot.ping_history.pop(0)

    avg_ping = round(sum(bot.ping_history) / len(bot.ping_history))
    stability = (
        "🟢 Excellente" if avg_ping <= 115 else
        "🟠 Moyenne" if avg_ping <= 200 else
        "🔴 Mauvaise"
    )

    up = timedelta(seconds=int(uptime.total_seconds()))
    days, remainder = divmod(up.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{int(days)}j {int(hours)}h {int(minutes)}m {int(seconds)}s"

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(bot.ping_history, marker='o', color=status["graph"], linewidth=2)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    ax.set_title("📶 Historique de la latence", fontsize=14, color='black')
    ax.set_xlabel("Mise à jour", color='black')
    ax.set_ylabel("Ping (ms)", color='black')
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#CCCCCC')

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    file = discord.File(buf, filename="ping_graph.png")
    plt.close()

    embed = discord.Embed(
        title="Statut de Project : Delta",
        description=status["emoji"] + f" Statut : {status['text']}",
        color=status["color"],
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_image(url="attachment://ping_graph.png")

    embed.add_field(name="🌐 Réseau", value=f"{len(bot.guilds):,} serveurs\n{total_members:,} membres", inline=True)
    embed.add_field(name="📶 Latence", value=f"{ping} ms", inline=True)
    embed.add_field(name="🕰 Uptime", value=f"{uptime_str}", inline=True)
    embed.add_field(name="📊 Stabilité", value=f"{stability}", inline=True)
    embed.add_field(name="💻 Commandes", value=f"{total_commands}", inline=True)
    embed.add_field(
        name="⚙️ Versions",
        value=f"Python : {platform.python_version()}\nDiscord.py : {discord.__version__}",
        inline=False
    )
    embed.set_footer(
        text="🔁 Actualisation automatique • Merci de faire confiance à Delta.",
        icon_url=bot.user.display_avatar.url
    )

    try:
        if message_id:
            msg = await channel.fetch_message(message_id)
            await msg.edit(embed=embed, attachments=[file])
        else:
            msg = await channel.send(embed=embed, file=file)
            bot.db_collections["delta_statut"].update_one(
                {"_id": "statut_embed"},
                {"$set": {"message_id": msg.id}},
                upsert=True
            )
        await msg.clear_reactions()
        await msg.add_reaction(discord.PartialEmoji.from_str(status["emoji"]))
    except (discord.NotFound, discord.Forbidden) as e:
        print("Erreur d'envoi ou de réaction :", e)

    # Gestion des alertes critiques
    if alert_triggered:
        alert_doc = bot.db_collections["delta_statut"].find_one({"_id": "critical_alert"})
        if not alert_doc:
            mention_roles = f"<@&{bot.config_ids['STAFF_PROJECT']}> <@&{bot.config_ids['STAFF_DELTA']}>"
            alert_embed = discord.Embed(
                title="🚨 ALERTE DE LATENCE CRITIQUE 🚨",
                description=(
                    f"{status['emoji']} **Ping moyen anormalement élevé depuis 3 cycles consécutifs !**\n\n"
                    f"📶 **Ping actuel :** {ping}ms\n"
                    "🛠️ **Action recommandée :** Vérifiez l'état de l'hébergement ou les services Discord.\n\n"
                    "⚠️ **Veuillez limiter l'utilisation du bot pendant cette période** afin d'éviter d'aggraver les performances."
                ),
                color=discord.Color.from_rgb(255, 45, 45),
                timestamp=datetime.utcnow()
            )
            alert_embed.set_footer(
                text="Surveillance automatique du système - Project : Delta",
                icon_url="IMAGES Delta/téléchargement (11).png"
            )
            alert_embed.set_thumbnail(url="https://www.saint-aignan-grandlieu.fr/fileadmin/Actualites/Alerte_-_Info/Alerte_info_image.jpg")
            alert_msg = await channel.send(
                content=mention_roles,
                embed=alert_embed,
                allowed_mentions=discord.AllowedMentions(roles=True)
            )
            bot.db_collections["delta_statut"].update_one(
                {"_id": "critical_alert"},
                {"$set": {"message_id": alert_msg.id}},
                upsert=True
            )
    else:
        alert_doc = bot.db_collections["delta_statut"].find_one({"_id": "critical_alert"})
        if alert_doc and "message_id" in alert_doc:
            try:
                alert_msg = await channel.fetch_message(alert_doc["message_id"])
                await alert_msg.delete()
            except discord.NotFound:
                print("Le message d'alerte n'existe plus.")
            except discord.Forbidden:
                print("Permissions insuffisantes pour supprimer le message d'alerte.")
            bot.db_collections["delta_statut"].delete_one({"_id": "critical_alert"})

    # Mise à jour du nom du salon
    new_name = f"︱{status['channel_emoji']}・𝖲tatut"
    if channel.name != new_name:
        try:
            await channel.edit(name=new_name)
        except discord.Forbidden:
            print("Permissions insuffisantes pour renommer le salon.")

    # Mise à jour du message de mise à jour
    now = datetime.now(ZoneInfo("Europe/Paris"))
    last_update_str = now.strftime("%d/%m/%Y à %H:%M:%S")
    update_text = f"<a:heart_d:1376837986381205535> **Dernière mise à jour :** {last_update_str}\n"

    update_data = bot.db_collections["delta_statut"].find_one({"_id": "update_info"})
    update_message_id = update_data.get("message_id") if update_data else None

    try:
        if update_message_id:
            update_msg = await channel.fetch_message(update_message_id)
            await update_msg.edit(content=update_text)
        else:
            update_msg = await channel.send(content=update_text)
            bot.db_collections["delta_statut"].update_one(
                {"_id": "update_info"},
                {"$set": {"message_id": update_msg.id}},
                upsert=True
            )
    except (discord.NotFound, discord.Forbidden) as e:
        print("Erreur d'envoi du message de mise à jour :", e)

async def update_status_embed_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await update_status_embed()
        wait_time = random.randint(5, 20)
        print(f"[Statut] Prochaine mise à jour dans {wait_time} minutes.")
        await asyncio.sleep(wait_time * 60)

# Tâche de fond toutes les 2 minutes
@tasks.loop(minutes=2)
async def update_dashboard():
    total_users = sum(guild.member_count for guild in bot.guilds)

    stats = {
        "_id": "global_stats",
        "guild_count": len(bot.guilds),
        "total_users": total_users,
        "commands_executed_today": bot.command_count,
        "last_update": datetime.utcnow()
    }

    bot.db_collections["ds_stats"].update_one(
        {"_id": "global_stats"},
        {"$set": stats},
        upsert=True
    )
    print("📊 Statistiques mises à jour dans MongoDB.")

# Chargement des cogs
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Cog {filename[:-3]} chargé.")
            except Exception as e:
                print(f"❌ Erreur lors du chargement du cog {filename[:-3]}: {e}")
                traceback.print_exc()

# Événement quand le bot est prêt
@bot.event
async def on_ready():
    print(f"✅ Le bot {bot.user} est maintenant connecté ! (ID: {bot.user.id})")

    # Démarrer les tâches de fond
    bot.uptime = time.time()
    update_dashboard.start()
    update_stats.start()
    urgence_ping_loop.start()
    update_bot_presence.start()
    envoyer_ping.start()
    bot.loop.create_task(update_status_embed_loop())

    guild_count = len(bot.guilds)
    member_count = sum(guild.member_count for guild in bot.guilds)

    print(f"\n📊 **Statistiques du bot :**")
    print(f"➡️ **Serveurs** : {guild_count}")
    print(f"➡️ **Utilisateurs** : {member_count}")

    activity_types = [
        discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} Membres"),
        discord.Activity(type=discord.ActivityType.streaming, name=f"{guild_count} Serveurs"),
        discord.Activity(type=discord.ActivityType.streaming, name="Project : Delta"),
    ]

    status_types = [discord.Status.online, discord.Status.idle, discord.Status.dnd]

    await bot.change_presence(
        activity=random.choice(activity_types),
        status=random.choice(status_types)
    )

    print(f"\n🎉 **{bot.user}** est maintenant connecté et affiche ses statistiques dynamiques avec succès !")
    print("📌 Commandes disponibles 😊")
    for command in bot.commands:
        print(f"- {command.name}")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Commandes slash synchronisées : {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation des commandes slash : {e}")

    # Charger les paramètres de tous les serveurs
    for guild in bot.guilds:
        bot.GUILD_SETTINGS[guild.id] = load_guild_settings(guild.id)

    # Charger les cogs après que le bot soit prêt
    await load_extensions()

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Une erreur s'est produite : {event}")
    embed = discord.Embed(
        title="❗ Erreur inattendue",
        description="Une erreur s'est produite lors de l'exécution de la commande. Veuillez réessayer plus tard.",
        color=discord.Color.red()
    )

    if isinstance(args[0], discord.Interaction):
        await args[0].response.send_message(embed=embed)
    elif isinstance(args[0], discord.Message):
        await args[0].channel.send(embed=embed)
    elif isinstance(args[0], discord.abc.GuildChannel):
        if isinstance(args[0], discord.TextChannel):
            await args[0].send(embed=embed)
        else:
            text_channel = discord.utils.get(args[0].guild.text_channels, name='ton-salon-textuel')
            if text_channel:
                await text_channel.send(embed=embed)
            else:
                print("Erreur : Aucun salon textuel trouvé pour envoyer l'embed.")
    else:
        print("Erreur : Le type de l'objet n'est pas pris en charge pour l'envoi du message.")

# Nécessaire pour que le bouton fonctionne après redémarrage
@bot.event
async def setup_hook():
    # Initialiser les vues persistantes ici si nécessaire
    # Par exemple, si vous avez des vues qui doivent être réactivées après un redémarrage
    # bot.add_view(UrgencyClaimView(message=None, detected_word=None)) # Exemple, ajustez selon vos besoins
    pass

# Token pour démarrer le bot (à partir des secrets)
keep_alive()
bot.run(token)