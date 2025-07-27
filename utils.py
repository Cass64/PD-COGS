import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import random
import re
import pytz
from typing import Optional

# Définition des IDs et collections (à passer depuis bot.py)
# Ces variables seront initialisées dans bot.py et passées aux cogs via bot.db_collections et bot.config_ids
# Pour l'instant, je les mets ici pour que les fonctions utilitaires puissent les référencer.
# Elles seront remplacées par des accès via `bot.db_collections` et `bot.config_ids` dans les cogs.
db_collections = {}
config_ids = {}

# Fonctions utilitaires
def create_embed(title, description, color=discord.Color.blue(), footer_text=""):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=footer_text)
    return embed

def has_permission(ctx, perm):
    # Vérifie si l'utilisateur a la permission spécifiée ou s'il est l'owner du bot
    return ctx.author.id == config_ids.get("ISEY_ID") or getattr(ctx.author.guild_permissions, perm, False)

def is_higher_or_equal(ctx, member):
    # Vérifie si le rôle de l'auteur est supérieur ou égal à celui du membre ciblé
    return member.top_role >= ctx.author.top_role

async def send_log(ctx, member, action, reason, duration=None):
    # Cette fonction devra être adaptée pour utiliser les IDs de log_channels
    # qui sont maintenant dans bot.config_ids ou une structure similaire.
    # Pour l'exemple, je vais utiliser un ID générique ou un print.
    # Dans un vrai bot, vous auriez une logique pour trouver le bon canal de log.
    log_channel_id = config_ids.get("WARN_LOG_CHANNEL") # Exemple
    if log_channel_id:
        log_channel = ctx.guild.get_channel(log_channel_id)
        if log_channel:
            embed = create_embed("🚨 Sanction appliquée", f"{member.mention} a été sanctionné.", discord.Color.red(), ctx, member, action, reason, duration)
            await log_channel.send(embed=embed)
    else:
        print(f"LOG: {member.name} {action} for {reason} (Duration: {duration})")

async def send_dm(member, action, reason, duration=None):
    try:
        embed = create_embed("🚨 Vous avez reçu une sanction", "Consultez les détails ci-dessous.", discord.Color.red())
        embed.add_field(name="⚖️ Sanction", value=action, inline=True)
        embed.add_field(name="📜 Raison", value=reason, inline=False)
        if duration:
            embed.add_field(name="⏳ Durée", value=duration, inline=True)
        await member.send(embed=embed)
    except discord.Forbidden:
        print(f"Impossible d'envoyer un DM à {member.display_name}.")

def load_guild_settings(guild_id: int) -> dict:
    # Récupère la configuration spécifique au serveur à partir de la base MongoDB
    # Cette fonction doit être appelée avec la collection appropriée
    return db_collections.get("presentation", {}).find_one({'guild_id': guild_id}) or {}

def get_premium_servers():
    """Récupère les IDs des serveurs premium depuis la base de données."""
    premium_docs = db_collections.get("setup_premium", {}).find({}, {"_id": 0, "guild_id": 1})
    return {doc["guild_id"] for doc in premium_docs}

async def is_blacklisted(user_id: int) -> bool:
    result = db_collections.get("delta_bl", {}).find_one({"user_id": str(user_id)})
    return result is not None

def add_sanction(guild_id, user_id, action, reason, duration=None):
    sanction_data = {
        "guild_id": guild_id,
        "user_id": user_id,
        "action": action,
        "reason": reason,
        "duration": duration,
        "timestamp": datetime.utcnow()
    }
    db_collections.get("sanction", {}).insert_one(sanction_data)

def get_log_channel(guild, key):
    # Cette fonction dépendra de la structure de vos IDs de log_channels
    # Pour l'instant, elle est simplifiée.
    log_channel_id = {
        "sanctions": config_ids.get("WARN_LOG_CHANNEL"),
        "messages": None, # Ajoutez les IDs réels ici
        # ... autres clés
    }.get(key)
    if log_channel_id:
        return guild.get_channel(log_channel_id)
    return None

def get_cf_config(guild_id):
    config = db_collections.get("idees", {}).find_one({"guild_id": guild_id})
    if not config:
        config = {
            "guild_id": guild_id,
            "start_chance": 50,
            "max_chance": 100,
            "max_bet": 20000
        }
        db_collections.get("idees", {}).insert_one(config)
    return config

def get_presentation_channel_id(guild_id: int):
    data = db_collections.get("presentation", {}).find_one({"guild_id": guild_id})
    return data.get("presentation_channel") if data else None

def get_user_partner_info(user_id: str):
    partner_data = db_collections.get("partner", {}).find_one({"user_id": user_id})
    if partner_data:
        return partner_data['rank'], partner_data['partnerships']
    return None, None

async def get_protection_data(guild_id):
    data = db_collections.get("protection", {}).find_one({"guild_id": str(guild_id)})
    return data or {}

def format_mention(id, type_mention):
    if not id or id == "Non défini":
        return "❌ **Non défini**"
    if isinstance(id, int) or (isinstance(id, str) and id.isdigit()):
        if type_mention == "user":
            return f"<@{id}>"
        elif type_mention == "role":
            return f"<@&{id}>"
        elif type_mention == "channel":
            return f"<#{id}>"
        return "❌ **Mention invalide**"
    return "❌ **Format invalide**"

PROTECTIONS = [
    "anti_massban", "anti_masskick", "anti_bot", "anti_createchannel",
    "anti_deletechannel", "anti_createrole", "anti_deleterole",
    "anti_everyone", "anti_spam", "anti_links", "whitelist"
]

PROTECTION_DETAILS = {
    "anti_massban": ("🚫 Anti-MassBan", "Empêche les bannissements massifs."),
    "anti_masskick": ("👢 Anti-MassKick", "Empêche les expulsions massives."),
    "anti_bot": ("🤖 Anti-Bot", "Bloque l'ajout de bots non autorisés."),
    "anti_createchannel": ("📤 Anti-Création de salon", "Empêche la création non autorisée de salons."),
    "anti_deletechannel": ("📥 Anti-Suppression de salon", "Empêche la suppression non autorisée de salons."),
    "anti_createrole": ("➕ Anti-Création de rôle", "Empêche la création non autorisée de rôles."),
    "anti_deleterole": ("➖ Anti-Suppression de rôle", "Empêche la suppression non autorisée de rôles."),
    "anti_everyone": ("📣 Anti-Everyone", "Empêche l'utilisation abusive de @everyone ou @here."),
    "anti_spam": ("💬 Anti-Spam", "Empêche le spam excessif de messages."),
    "anti_links": ("🔗 Anti-Liens", "Empêche l'envoi de liens non autorisés."),
    "whitelist": ("✅ Liste blanche", "Utilisateurs exemptés des protections.")
}

def generate_global_status_bar(data: dict) -> str:
    protections = [prot for prot in PROTECTIONS if prot != "whitelist"]
    total = len(protections)
    enabled_count = sum(1 for prot in protections if data.get(prot, False))
    ratio = enabled_count / total

    bar_length = 10
    filled_length = round(bar_length * ratio)
    bar = "🟩" * filled_length + "⬛" * (bar_length - filled_length)
    return f"**Sécurité Globale :** `{enabled_count}/{total}`\n{bar}"

def format_protection_field(prot, data, guild, bot):
    name, desc = PROTECTION_DETAILS[prot]
    enabled = data.get(prot, False)
    status = "✅ Activée" if enabled else "❌ Désactivée"
    updated_by_id = data.get(f"{prot}_updated_by")
    updated_at = data.get(f"{prot}_updated_at")

    modifier = None
    if updated_by_id:
        modifier = guild.get_member(int(updated_by_id)) or updated_by_id

    formatted_date = ""
    if updated_at:
        dt = updated_at.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Europe/Paris"))
        formatted_date = f"🕓 {dt.strftime('%d/%m/%Y à %H:%M')}"

    mod_info = f"\n👤 Modifié par : {modifier.mention if isinstance(modifier, discord.Member) else modifier}" if modifier else ""
    date_info = f"\n{formatted_date}" if formatted_date else ""

    value = f"> {desc}\n> **Statut :** {status}{mod_info}{date_info}"
    return name, value

async def notify_owner_of_protection_change(guild, prot, new_value, interaction):
    if guild and guild.owner:
        try:
            embed = discord.Embed(
                title="🔐 Mise à jour d'une protection sur votre serveur",
                description=f"**Protection :** {PROTECTION_DETAILS[prot][0]}\n"
                            f"**Statut :** {'✅ Activée' if new_value else '❌ Désactivée'}",
                color=discord.Color.green() if new_value else discord.Color.red()
            )
            embed.add_field(
                name="👤 Modifiée par :",
                value=f"{interaction.user.mention} (`{interaction.user}`)",
                inline=False
            )
            embed.add_field(name="🏠 Serveur :", value=guild.name, inline=False)
            embed.add_field(
                name="🕓 Date de modification :",
                value=f"<t:{int(datetime.utcnow().timestamp())}:f>",
                inline=False
            )
            embed.add_field(
                name="ℹ️ Infos supplémentaires :",
                value="Vous pouvez reconfigurer vos protections à tout moment avec la commande `/protection`.",
                inline=False
            )

            await guild.owner.send(embed=embed)
        except discord.Forbidden:
            print("Impossible d’envoyer un DM à l’owner.")
        except Exception as e:
            print(f"Erreur lors de l'envoi du DM : {e}")

def is_admin_or_isey():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or ctx.author.id == config_ids.get("ISEY_ID")
    return commands.check(predicate)

THUMBNAIL_URL = "images_GITHUB/3e3bd3c24e33325c7088f43c1ae0fadc.png" # Chemin corrigé

# 🎭 Emojis dynamiques pour chaque serveur
EMOJIS_SERVEURS = ["🌍", "🚀", "🔥", "👾", "🏆", "🎮", "🏴‍☠️", "🏕️"]

# ⚜️ ID du serveur Etherya
ETHERYA_ID = 1034007767050104892 # Utiliser l'ID réel si différent

def boost_bar(level):
    """Génère une barre de progression pour le niveau de boost."""
    filled = "🟣" * level
    empty = "⚫" * (3 - level)
    return filled + empty

# Dictionnaire pour stocker les messages supprimés {channel_id: deque[(timestamp, auteur, contenu)]}
sniped_messages = defaultdict(deque)

# Liste des catégories sensibles
sensitive_categories = {
    "insultes_graves": ["fils de pute"],
    "discours_haineux": ["nigger", "nigga", "negro", "chintok", "bougnoule", "pédé","sale pédé","sale arabe", "sale noir", "sale juif", "sale blanc", "race inférieure", "sale race", "enculé de ta race", "triso"],
    "ideologies_haineuses": ["raciste", "homophobe", "xénophobe", "transphobe", "antisémite", "islamophobe", "suprémaciste", "fasciste", "nazi", "néonazi", "dictateur", "extrémiste", "fanatique", "radicalisé", "djihadiste"],
    "violences_crimes": ["viol", "pédophilie", "inceste", "pédocriminel", "grooming", "agression", "assassin", "meurtre", "homicide", "génocide", "extermination", "décapitation", "lynchage", "massacre", "torture", "suicidaire", "prise d'otage", "terrorisme", "attentat", "bombardement", "exécution", "immolation", "traite humaine", "esclavage sexuel", "kidnapping", "tueur en série", "infanticide", "parricide"],
    "drogues_substances": ["cocaïne", "héroïne", "crack", "LSD", "ecstasy", "GHB", "fentanyl", "méthamphétamine", "cannabis", "weed", "opium", "drogue", "drogue de synthèse", "trafic de drogue","overdose", "shooté", "stoned", "sniffer", "shit"],
    "contenus_sexuels": ["pornographie", "porno", "prostitution", "escort", "masturbation", "fellation", "pipe", "sodomie", "exhibition", "fétichisme", "orgie", "gode", "pénétration", "nudité", "camgirl", "onlyfans", "porno enfant", "sextape", "branlette", "bite",],
    "fraudes_financières": ["scam", "arnaque", "fraude", "chantage", "extorsion", "évasion fiscale", "fraude fiscale", "détournement de fonds","blanchiment d'argent", "crypto scam", "phishing bancaire", "vol d'identité", "usurpation"],
    "attaques_menaces": ["raid", "ddos", "dox", "doxx", "hack", "hacking", "botnet", "crash bot", "flood", "booter", "keylogger", "phishing", "malware", "trojan", "ransomware", "brute force", "cheval de troie", "injection SQL"],
    "raids_discord": ["mass ping", "raid bot", "join raid", "leaver bot", "spam bot", "token grabber", "auto join", "multi account", "alt token", "webhook spam", "webhook nuker", "selfbot", "auto spam"],
    "harcèlement_haine": ["swat", "swatting", "harass", "threaten", "kill yourself", "kys", "suicide", "death threat", "pedo", "grooming", "harcèlement", "cyberharcèlement", "intimidation", "menace de mort", "appel au suicide"],
    "personnages_problématiques": ["Hitler", "Mussolini", "Staline", "Pol Pot", "Mao Zedong", "Benito Mussolini", "Joseph Staline", "Adolf Hitler", "Kim Jong-il","Kim Jong-un", "Idi Amin", "Saddam Hussein", "Bachar el-Assad", "Ben Laden", "Oussama Ben Laden", "Ayman al-Zawahiri", "Heinrich Himmler", "Joseph Goebbels", "Hermann Göring", "Adolf Eichmann", "Rudolf Hess", "Slobodan Milošević", "Radovan Karadžić", "Ratko Mladić", "Francisco Franco", "Augusto Pinochet", "Fidel Castro", "Che Guevara", "Ayatollah Khomeini", "Al-Baghdadi", "Abu Bakr al-Baghdadi", "Anders Behring Breivik", "Charles Manson", "Ted Bundy", "Jeffrey Dahmer", "Richard Ramirez", "John Wayne Gacy", "Albert Fish", "Ed Gein", "Luca Magnotta", "Peter Kürten", "David Berkowitz", "Ariel Castro", "Yitzhak Shamir", "Meir Kahane", "Nicolae Ceaușescu", "Vladimir Poutine", "Alexander Lukashenko", "Mengistu Haile Mariam", "Yahya Jammeh", "Omar el-Béchir", "Jean-Bédel Bokassa", "Robert Mugabe", "Mobutu Sese Seko", "Laurent-Désiré Kabila", "Joseph Kony", "Enver Hoxha", "Gaddafi", "Muammar Kadhafi", "Ríos Montt", "Reinhard Heydrich", "Ismail Enver", "Anton Mussert", "Ante Pavelić", "Vidkun Quisling", "Stepan Bandera", "Ramush Haradinaj", "Slobodan Praljak", "Milomir Stakić", "Theodore Kaczynski", "Eric Harris", "Dylan Klebold", "Brenton Tarrant", "Seung-Hui Cho", "Stephen Paddock", "Patrick Crusius", "Elliot Rodger", "Nikolas Cruz", "Dylann Roof", "Timothy McVeigh", "Tamerlan Tsarnaev", "Dzhokhar Tsarnaev", "Sayfullo Saipov", "Mohamed Merah", "Amedy Coulibaly", "Chérif Kouachi", "Salah Abdeslam", "Abdelhamid Abaaoud", "Mohammed Atta", "Khalid Sheikh Mohammed", "Ramzi Yousef", "Richard Reid", "Umar Farouk Abdulmutallab", "Anwar al-Awlaki"]
}

word_to_category = {}
for category, words in sensitive_categories.items():
    for word in words:
        word_to_category[word.lower()] = category

# Dictionnaire global pour les cooldowns des sondages
user_cooldown = {}

# Dictionnaires pour les giveaways
giveaways = {}
ended_giveaways = {}
fast_giveaways = {}

# Dictionnaire pour les alertes d'urgence
active_alerts = {}

# Fonction pour vérifier si une URL est valide
def is_valid_url(url):
    regex = re.compile(
        r'^(https?://)?'  # http:// ou https:// (optionnel)
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # domaine
        r'(/.*)?$'  # chemin (optionnel)
    )
    return bool(re.match(regex, url))

# Pour les stats globales
stats_collection33 = None # Sera initialisé dans bot.py

