import discord
from discord.ext import commands
from discord import app_commands, Embed, ButtonStyle, ui
from discord.ui import Button, View, Select, Modal, TextInput, SelectOption
from datetime import datetime, timedelta, timezone
import asyncio
import random
import re
import platform

from utils import (
    create_embed, has_permission, is_higher_or_equal, send_log, send_dm,
    load_guild_settings, get_premium_servers, is_blacklisted, add_sanction,
    get_log_channel, get_cf_config, get_presentation_channel_id, get_user_partner_info,
    get_protection_data, format_mention, generate_global_status_bar, format_protection_field,
    notify_owner_of_protection_change, is_valid_url, is_admin_or_isey,
    THUMBNAIL_URL, EMOJIS_SERVEURS, ETHERYA_ID, boost_bar, sensitive_categories,
    word_to_category, active_alerts, giveaways, ended_giveaways, fast_giveaways,
    user_cooldown, sniped_messages, stats_collection33, PROTECTIONS, PROTECTION_DETAILS
)

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collection = bot.db_collections["setup"]
        self.collection2 = bot.db_collections["setup_premium"]
        self.collection4 = bot.db_collections["protection"]
        self.collection8 = bot.db_collections["idees"]
        self.collection9 = bot.db_collections["stats"]
        self.collection19 = bot.db_collections["wl"]
        self.collection20 = bot.db_collections["suggestions"]
        self.collection21 = bot.db_collections["presentation"]
        self.collection22 = bot.db_collections["absence"]
        self.collection25 = bot.db_collections["delta_bl"]
        self.collection27 = bot.db_collections["guild_troll"]
        self.collection28 = bot.db_collections["sensible"]
        self.config_ids = bot.config_ids

    @commands.command()
    async def vc(self, ctx):
        try:
            guild = ctx.guild
            total_members = guild.member_count
            online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
            voice_members = sum(len(voice_channel.members) for voice_channel in guild.voice_channels)
            boosts = guild.premium_subscription_count or 0
            owner_member = guild.owner
            verification_level = guild.verification_level.name
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            server_created_at = guild.created_at.strftime('%d %B %Y')

            invites = await guild.invites()
            if invites:
                server_invite = invites[0].url
            else:
                server_invite = await guild.text_channels[0].create_invite(max_age=86400)

            embed = create_embed(f"📊 Statistiques de {guild.name}", "", discord.Color.purple())
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            embed.add_field(name="👥 Membres", value=f"**{total_members}**", inline=True)
            embed.add_field(name="🟢 Membres en ligne", value=f"**{online_members}**", inline=True)
            embed.add_field(name="🎙️ En vocal", value=f"**{voice_members}**", inline=True)
            embed.add_field(name="💎 Boosts", value=f"**{boosts}**", inline=True)
            embed.add_field(name="👑 Propriétaire", value=f"<@{owner_member.id}>", inline=True)
            embed.add_field(name="🔒 Niveau de vérification", value=f"**{verification_level}**", inline=True)
            embed.add_field(name="📝 Canaux textuels", value=f"**{text_channels}**", inline=True)
            embed.add_field(name="🔊 Canaux vocaux", value=f"**{voice_channels}**", inline=True)
            embed.add_field(name="📅 Créé le", value=f"**{server_created_at}**", inline=False)
            embed.add_field(name="🔗 Lien du serveur", value=f"[{guild.name}]({server_invite})", inline=False)
            embed.set_footer(text="📈 Statistiques mises à jour en temps réel | ♥️ by Iseyg")

            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande 'vc': {e}")
            await ctx.send("Une erreur est survenue lors de l'exécution de la commande.")

    @app_commands.command(name="ping", description="Affiche le Ping du bot.")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = create_embed("Pong!", f"Latence: {latency}ms", discord.Color.green())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info-rôle", description="Obtenez des informations détaillées sur un rôle")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        if role is None:
            embed = create_embed("Erreur", "Rôle introuvable.", discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        else:
            sorted_roles = sorted(interaction.guild.roles, key=lambda r: r.position, reverse=True)
            total_roles = len(sorted_roles)
            inverse_position = total_roles - sorted_roles.index(role)

            embed = create_embed(
                f"Informations sur le rôle: {role.name}",
                "",
                role.color
            )
            embed.timestamp = interaction.created_at
            embed.set_thumbnail(url=interaction.guild.icon.url)
            embed.add_field(name="ID", value=role.id, inline=False)
            embed.add_field(name="Couleur", value=str(role.color), inline=False)
            embed.add_field(name="Nombre de membres", value=len(role.members), inline=False)
            embed.add_field(name="Position dans la hiérarchie", value=f"{inverse_position}/{total_roles}", inline=False)
            embed.add_field(name="Mentionnable", value=role.mentionable, inline=False)
            embed.add_field(name="Gérer les permissions", value=role.managed, inline=False)
            embed.add_field(name="Créé le", value=role.created_at.strftime("%d/%m/%Y à %H:%M:%S"), inline=False)
            embed.add_field(name="Mention", value=role.mention, inline=False)
            embed.set_footer(text=f"Commande demandée par {interaction.user.name}", icon_url=interaction.user.avatar.url)

            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="uptime", description="Affiche l'uptime du bot.")
    async def uptime(self, interaction: discord.Interaction):
        uptime_seconds = round(time.time() - self.bot.uptime)
        days = uptime_seconds // (24 * 3600)
        hours = (uptime_seconds % (24 * 3600)) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        embed = create_embed(
            "Uptime du bot",
            f"Le bot est en ligne depuis : {days} jours, {hours} heures, {minutes} minutes, {seconds} secondes",
            discord.Color.blue()
        )
        embed.set_footer(text=f"♥️by Iseyg", icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="calcul", description="Effectue une opération mathématique")
    @app_commands.describe(nombre1="Le premier nombre", operation="L'opération à effectuer (+, -, *, /)", nombre2="Le deuxième nombre")
    async def calcul(self, interaction: discord.Interaction, nombre1: float, operation: str, nombre2: float):
        await interaction.response.defer()
        resultat = None
        if operation == "+":
            resultat = nombre1 + nombre2
        elif operation == "-":
            resultat = nombre1 - nombre2
        elif operation == "*":
            resultat = nombre1 * nombre2
        elif operation == "/":
            if nombre2 != 0:
                resultat = nombre1 / nombre2
            else:
                await interaction.followup.send("❌ Erreur : Division par zéro impossible.")
                return
        else:
            await interaction.followup.send("❌ Opération invalide. Utilisez '+', '-', '*', ou '/'.")
            return

        embed = create_embed(
            "📊 Résultat du calcul",
            f"{nombre1} {operation} {nombre2} = **{resultat}**",
            discord.Color.green()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="calcul-pourcentage", description="Calcule un pourcentage d'un nombre")
    @app_commands.describe(nombre="Le nombre de base", pourcentage="Le pourcentage à appliquer (ex: 15 pour 15%)")
    async def calcul_pourcentage(self, interaction: discord.Interaction, nombre: float, pourcentage: float):
        await interaction.response.defer()
        resultat = (nombre * pourcentage) / 100
        embed = create_embed(
            "📊 Calcul de pourcentage",
            f"{pourcentage}% de {nombre} = **{resultat}**",
            discord.Color.green()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="connect", description="Connecte le bot à un salon vocal spécifié.")
    @app_commands.describe(channel="Choisissez un salon vocal où connecter le bot")
    @commands.has_permissions(administrator=True)
    async def connect(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        try:
            if not interaction.guild.voice_client:
                await channel.connect()
                embed = create_embed(
                    "✅ Connexion réussie !",
                    f"Le bot a rejoint **{channel.name}**.",
                    discord.Color.green()
                )
                await interaction.response.send_message(embed=embed)
            else:
                embed = create_embed(
                    "⚠️ Déjà connecté",
                    "Le bot est déjà dans un salon vocal.",
                    discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = create_embed(
                "❌ Erreur",
                f"Une erreur est survenue : `{e}`",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="disconnect", description="Déconnecte le bot du salon vocal.")
    @commands.has_permissions(administrator=True)
    async def disconnect(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            embed = create_embed(
                "🚫 Déconnexion réussie",
                "Le bot a quitté le salon vocal.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = create_embed(
                "⚠️ Pas connecté",
                "Le bot n'est dans aucun salon vocal.",
                discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="idée", description="Rajoute une idée dans la liste")
    async def ajouter_idee(self, interaction: discord.Interaction, idee: str):
        user_id = interaction.user.id
        idees_data = self.collection8.find_one({"user_id": str(user_id)})

        if idees_data:
            self.collection8.update_one(
                {"user_id": str(user_id)},
                {"$push": {"idees": idee}}
            )
        else:
            self.collection8.insert_one({
                "user_id": str(user_id),
                "idees": [idee]
            })
        embed = create_embed("Idée ajoutée !", f"**{idee}** a été enregistrée.", discord.Color.green())
        await interaction.response.send_message(embed=embed)

    @commands.command(name="listi")
    async def liste_idees(self, ctx):
        user_id = ctx.author.id
        idees_data = self.collection8.find_one({"user_id": str(user_id)})

        if not idees_data or not idees_data.get("idees"):
            embed = create_embed("Aucune idée enregistrée", "Ajoute-en une avec `/idée` !", discord.Color.red())
        else:
            embed = create_embed("Tes idées", "", discord.Color.blue())
            for idx, idee in enumerate(idees_data["idees"], start=1):
                embed.add_field(name=f"Idée {idx}", value=idee, inline=False)
        await ctx.send(embed=embed)

    @app_commands.command(name="remove-idee", description="Supprime une de tes idées enregistrées")
    async def remove_idee(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        idees_data = self.collection8.find_one({"user_id": str(user_id)})

        if not idees_data or not idees_data.get("idees"):
            embed = create_embed("Aucune idée enregistrée", "Ajoute-en une avec `/idée` !", discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return

        idees = idees_data["idees"]
        options = [discord.SelectOption(label=f"Idée {idx+1}: {idee}", value=str(idx)) for idx, idee in enumerate(idees)]

        select = Select(placeholder="Choisis une idée à supprimer", options=options)

        async def select_callback(interaction: discord.Interaction):
            selected_idee_index = int(select.values[0])
            idee_a_supprimer = idees[selected_idee_index]

            self.collection8.update_one(
                {"user_id": str(user_id)},
                {"$pull": {"idees": idee_a_supprimer}}
            )
            embed = create_embed(
                "Idée supprimée !",
                f"L'idée **{idee_a_supprimer}** a été supprimée.",
                discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

        select.callback = select_callback
        view = View()
        view.add_item(select)
        embed = create_embed(
            "Choisis l'idée à supprimer",
            "Sélectionne une idée à supprimer dans le menu déroulant.",
            discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, view=view)

    class SuggestionModal(Modal):
        def __init__(self, bot_instance):
            super().__init__(title="💡 Nouvelle Suggestion")
            self.bot = bot_instance
            self.suggestion_input = TextInput(
                label="Entrez votre suggestion",
                style=discord.TextStyle.paragraph,
                placeholder="Écrivez ici...",
                required=True,
                max_length=1000
            )
            self.add_item(self.suggestion_input)

        async def on_submit(self, interaction: discord.Interaction):
            guild_id = str(interaction.guild.id)
            data = self.bot.db_collections["suggestions"].find_one({"guild_id": guild_id})

            if not data or "suggestion_channel_id" not in data or "suggestion_role_id" not in data:
                return await interaction.response.send_message("❌ Le salon ou le rôle des suggestions n'a pas été configuré.", ephemeral=True)

            channel = interaction.client.get_channel(int(data["suggestion_channel_id"]))
            role = interaction.guild.get_role(int(data["suggestion_role_id"]))

            if not channel or not role:
                return await interaction.response.send_message("❌ Impossible de trouver le salon ou le rôle configuré.", ephemeral=True)

            embed = create_embed(
                "💡 Nouvelle Suggestion",
                self.suggestion_input.value,
                discord.Color.green()
            )
            embed.set_footer(text=f"Suggéré par {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
            embed.timestamp = datetime.utcnow()

            sent_message = await channel.send(
                content=f"{role.mention} 🚀 Une nouvelle suggestion a été soumise !",
                embed=embed
            )

            await sent_message.edit(view=Utility.SuggestionView(message_id=sent_message.id))

            await interaction.response.send_message("✅ Votre suggestion a été envoyée avec succès !", ephemeral=True)

    class CommentModal(Modal):
        def __init__(self, original_message_id: int, bot_instance):
            super().__init__(title="💬 Commenter une suggestion")
            self.message_id = original_message_id
            self.bot = bot_instance
            self.comment_input = TextInput(
                label="Votre commentaire",
                placeholder="Exprimez votre avis ou amélioration...",
                style=discord.TextStyle.paragraph,
                max_length=500
            )
            self.add_item(self.comment_input)

        async def on_submit(self, interaction: discord.Interaction):
            guild_id = str(interaction.guild.id)
            data = self.bot.db_collections["suggestions"].find_one({"guild_id": guild_id})

            if not data or "suggestion_channel_id" not in data:
                return await interaction.response.send_message("❌ Le salon de suggestion est mal configuré.", ephemeral=True)

            channel = interaction.client.get_channel(int(data["suggestion_channel_id"]))
            if not channel:
                return await interaction.response.send_message("❌ Le salon de suggestion est introuvable.", ephemeral=True)

            comment_embed = create_embed(
                "🗨️ Nouveau commentaire sur une suggestion",
                self.comment_input.value,
                discord.Color.blurple()
            )
            comment_embed.set_footer(text=f"Par {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
            comment_embed.timestamp = datetime.utcnow()

            await channel.send(content=f"📝 Commentaire sur la suggestion ID `{self.message_id}` :", embed=comment_embed)
            await interaction.response.send_message("✅ Commentaire envoyé avec succès !", ephemeral=True)

    class SuggestionView(View):
        def __init__(self, message_id: int):
            super().__init__(timeout=None)
            self.message_id = message_id
            self.add_item(Button(label="✅ Approuver", style=discord.ButtonStyle.green, custom_id="suggestion_approve"))
            self.add_item(Button(label="❌ Refuser", style=discord.ButtonStyle.red, custom_id="suggestion_decline"))
            self.add_item(Button(label="💬 Commenter", style=discord.ButtonStyle.blurple, custom_id=f"suggestion_comment:{message_id}"))

    @app_commands.command(name="suggestion", description="💡 Envoie une suggestion pour le serveur")
    async def suggest(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        data = self.bot.db_collections["suggestions"].find_one({"guild_id": guild_id})

        if not data or "suggestion_channel_id" not in data or "suggestion_role_id" not in data:
            return await interaction.response.send_message("❌ Le système de suggestion n'est pas encore configuré.", ephemeral=True)

        await interaction.response.send_modal(self.SuggestionModal(self.bot))

    @app_commands.command(name="set-suggestion", description="📝 Définir le salon et rôle pour les suggestions")
    @app_commands.describe(channel="Salon pour recevoir les suggestions", role="Rôle à ping lors des suggestions")
    @commands.has_permissions(administrator=True)
    async def set_suggestion(self, interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild.id)
        self.bot.db_collections["suggestions"].update_one(
            {"guild_id": guild_id},
            {"$set": {
                "suggestion_channel_id": str(channel.id),
                "suggestion_role_id": str(role.id)
            }},
            upsert=True
        )
        await interaction.followup.send(
            f"✅ Le système de suggestions est maintenant configuré avec {channel.mention} et {role.mention}.",
            ephemeral=True
        )

    @set_suggestion.error
    async def set_suggestion_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Tu n'as pas les permissions nécessaires.", ephemeral=True)
        else:
            print(f"Erreur dans set_suggestion: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    class PollModal(discord.ui.Modal, title="📊 Créer un sondage interactif"):
        def __init__(self):
            super().__init__()
            self.question = discord.ui.TextInput(
                label="💬 Question principale",
                placeholder="Ex : Quel est votre fruit préféré ?",
                max_length=200,
                style=discord.TextStyle.paragraph
            )
            self.options = discord.ui.TextInput(
                label="🧩 Choix possibles (séparés par des virgules)",
                placeholder="Ex : 🍎 Pomme, 🍌 Banane, 🍇 Raisin, 🍍 Ananas",
                max_length=300
            )
            self.add_item(self.question)
            self.add_item(self.options)

        async def on_submit(self, interaction: discord.Interaction):
            user_id = interaction.user.id
            if user_id in user_cooldown and time.time() - user_cooldown[user_id] < 60:
                return await interaction.response.send_message(
                    "⏳ Vous devez attendre **60 secondes** avant de créer un nouveau sondage.",
                    ephemeral=True
                )
            user_cooldown[user_id] = time.time()

            question = self.question.value
            options_raw = self.options.value
            options = [opt.strip() for opt in options_raw.split(",") if opt.strip()]

            if len(options) < 2 or len(options) > 10:
                return await interaction.response.send_message(
                    "❗ Veuillez entrer **entre 2 et 10 choix** maximum pour votre sondage.",
                    ephemeral=True
                )

            embed = create_embed(
                "📢 Nouveau sondage disponible !",
                (
                    f"🧠 **Question** :\n> *{question}*\n\n"
                    f"🎯 **Choix proposés** :\n" +
                    "\n".join([f"{chr(0x1F1E6 + i)} ┇ {opt}" for i, opt in enumerate(options)])
                ),
                discord.Color.teal()
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4140/4140047.png")
            embed.set_footer(text="Réagissez ci-dessous pour voter 🗳️")
            embed.timestamp = discord.utils.utcnow()

            message = await interaction.channel.send(embed=embed)
            for i in range(len(options)):
                await message.add_reaction(chr(0x1F1E6 + i))

            await interaction.response.send_message("✅ Votre sondage a été publié avec succès !", ephemeral=True)

    @app_commands.command(name="sondage", description="📊 Créez un sondage stylé avec des choix")
    async def sondage(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.PollModal())

    class PresentationForm(discord.ui.Modal, title="📝 Faisons connaissance"):
        def __init__(self, bot_instance):
            super().__init__()
            self.bot = bot_instance
            self.pseudo = TextInput(label="Ton pseudo", placeholder="Ex: Jean_57", required=True, max_length=50)
            self.age = TextInput(label="Ton âge", placeholder="Ex: 18", required=True, max_length=3)
            self.passion = TextInput(label="Ta passion principale", placeholder="Ex: Gaming, Musique...", required=True, max_length=100)
            self.bio = TextInput(label="Une courte bio", placeholder="Parle un peu de toi...", style=discord.TextStyle.paragraph, required=True, max_length=300)
            self.reseaux = TextInput(label="Tes réseaux sociaux préférés", placeholder="Ex: Twitter, TikTok, Discord...", required=False, max_length=100)
            self.add_item(self.pseudo)
            self.add_item(self.age)
            self.add_item(self.passion)
            self.add_item(self.bio)
            self.add_item(self.reseaux)

        async def on_submit(self, interaction: discord.Interaction):
            guild_id = interaction.guild.id
            guild_settings = load_guild_settings(guild_id) # Utilise la fonction utilitaire
            presentation_channel_id = guild_settings.get('presentation_channel')

            if presentation_channel_id:
                presentation_channel = interaction.guild.get_channel(presentation_channel_id)
                if presentation_channel:
                    embed = create_embed(
                        f"📢 Nouvelle présentation de {interaction.user.display_name}",
                        "Voici une nouvelle présentation ! 🎉",
                        discord.Color.blurple()
                    )
                    embed.set_thumbnail(url=interaction.user.display_avatar.url)
                    embed.add_field(name="👤 Pseudo", value=self.pseudo.value, inline=True)
                    embed.add_field(name="🎂 Âge", value=self.age.value, inline=True)
                    embed.add_field(name="🎨 Passion", value=self.passion.value, inline=False)
                    if self.reseaux.value:
                        embed.add_field(name="🌐 Réseaux sociaux", value=self.reseaux.value, inline=False)
                    embed.add_field(name="📝 Bio", value=self.bio.value, inline=False)
                    embed.set_footer(text=f"Utilisateur ID: {interaction.user.id}", icon_url=interaction.user.display_avatar.url)
                    embed.timestamp = datetime.utcnow()

                    await presentation_channel.send(embed=embed)
                    await interaction.response.send_message("Ta présentation a été envoyée ! 🎉", ephemeral=True)
                else:
                    await interaction.response.send_message("Le salon de présentation n'existe plus ou est invalide.", ephemeral=True)
            else:
                await interaction.response.send_message("Le salon de présentation n'a pas été configuré pour ce serveur.", ephemeral=True)

    @app_commands.command(name="presentation", description="Remplis un formulaire pour te présenter à la communauté !")
    async def presentation(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        guild_settings = load_guild_settings(guild_id)
        presentation_channel_id = guild_settings.get('presentation_channel')

        if presentation_channel_id:
            try:
                await interaction.response.send_modal(self.PresentationForm(self.bot))
            except discord.errors.HTTPException as e:
                print(f"Erreur lors de l'envoi du modal : {e}")
                await interaction.response.send_message("❌ Une erreur est survenue lors de l'envoi du formulaire. Veuillez réessayer.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "⚠️ Le salon de présentation n’a pas été configuré sur ce serveur. Veuillez contacter un administrateur.",
                ephemeral=True
            )

    @app_commands.command(name="set-presentation", description="Définit le salon où les présentations seront envoyées (admin uniquement)")
    @commands.has_permissions(administrator=True)
    async def set_presentation(self, interaction: discord.Interaction, salon: discord.TextChannel):
        guild_id = interaction.guild.id
        channel_id = salon.id
        self.bot.db_collections["presentation"].update_one(
            {"guild_id": guild_id},
            {"$set": {"presentation_channel": channel_id}},
            upsert=True
        )
        await interaction.response.send_message(
            f"✅ Le salon de présentation a bien été défini sur {salon.mention}.", ephemeral=True
        )

    @set_presentation.error
    async def set_presentation_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
        else:
            print(f"Erreur dans set_presentation: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    class ProtectionMenu(Select):
        def __init__(self, guild_id, protection_data, bot_instance):
            self.guild_id = guild_id
            self.protection_data = protection_data
            self.bot = bot_instance

            options = [
                discord.SelectOption(
                    label=PROTECTION_DETAILS[prot][0],
                    description="Activer ou désactiver cette protection.",
                    emoji="🔒" if protection_data.get(prot, False) else "🔓",
                    value=prot
                )
                for prot in PROTECTIONS if prot != "whitelist"
            ]
            super().__init__(
                placeholder="🔧 Choisissez une protection à modifier",
                min_values=1,
                max_values=1,
                options=options
            )

        async def callback(self, interaction: discord.Interaction):
            prot = self.values[0]
            current = self.protection_data.get(prot, False)
            new_value = not current

            self.bot.db_collections["protection"].update_one(
                {"guild_id": str(self.guild_id)},
                {"$set": {
                    prot: new_value,
                    f"{prot}_updated_by": str(interaction.user.id),
                    f"{prot}_updated_at": datetime.utcnow()
                }},
                upsert=True
            )

            self.protection_data[prot] = new_value
            self.protection_data[f"{prot}_updated_by"] = interaction.user.id
            self.protection_data[f"{prot}_updated_at"] = datetime.utcnow()

            guild = interaction.guild
            if guild and guild.owner:
                await notify_owner_of_protection_change(guild, prot, new_value, interaction)

            embed = create_embed("🛡️ Système de Protection", "", discord.Color.blurple())
            for p in PROTECTIONS:
                if p == "whitelist":
                    whitelist_data = self.bot.db_collections["wl"].find_one({"guild_id": str(self.guild_id)}) or {}
                    wl_users = whitelist_data.get("whitelist", [])
                    if not wl_users:
                        embed.add_field(name=PROTECTION_DETAILS[p][0], value="Aucun utilisateur whitelisté.", inline=False)
                    else:
                        members = []
                        for uid in wl_users:
                            user = interaction.guild.get_member(int(uid)) or await self.bot.fetch_user(int(uid))
                            members.append(f"- {user.mention if isinstance(user, discord.Member) else user.name}")
                        embed.add_field(name=PROTECTION_DETAILS[p][0], value="\n".join(members), inline=False)
                else:
                    name, value = format_protection_field(p, self.protection_data, guild, self.bot)
                    embed.add_field(name=name, value=value, inline=False)

            embed.add_field(
                name="🔒 Résumé des protections",
                value=generate_global_status_bar(self.protection_data),
                inline=False
            )
            embed.set_footer(text="🎚️ Sélectionnez une option ci-dessous pour gérer la sécurité du serveur.")
            view = View()
            view.add_item(Utility.ProtectionMenu(self.guild_id, self.protection_data, self.bot))
            await interaction.response.edit_message(embed=embed, view=view)

    class ProtectionView(View):
        def __init__(self, guild_id, protection_data, bot_instance):
            super().__init__(timeout=None)
            self.add_item(Utility.ProtectionMenu(guild_id, protection_data, bot_instance))

    @app_commands.command(name="protection", description="Configurer les protections du serveur")
    @is_admin_or_isey()
    async def protection(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        protection_data = self.collection4.find_one({"guild_id": guild_id}) or {}

        embed = create_embed("🛡️ Système de Protection", "", discord.Color.blurple())
        for prot in PROTECTIONS:
            if prot == "whitelist":
                whitelist_data = self.collection19.find_one({"guild_id": guild_id}) or {}
                wl_users = whitelist_data.get("whitelist", [])
                if not wl_users:
                    embed.add_field(name=PROTECTION_DETAILS[prot][0], value="Aucun utilisateur whitelisté.", inline=False)
                else:
                    members = []
                    for uid in wl_users:
                        user = interaction.guild.get_member(int(uid)) or await self.bot.fetch_user(int(uid))
                        members.append(f"- {user.mention if isinstance(user, discord.Member) else user.name}")
                    embed.add_field(name=PROTECTION_DETAILS[prot][0], value="\n".join(members), inline=False)
            else:
                name, value = format_protection_field(prot, protection_data, interaction.guild, self.bot)
                embed.add_field(name=name, value=value, inline=False)

        embed.add_field(
            name="🔒 Résumé des protections",
            value=generate_global_status_bar(protection_data),
            inline=False
        )
        embed.set_footer(text="🎚️ Sélectionnez une option ci-dessous pour gérer la sécurité du serveur.")
        view = Utility.ProtectionView(guild_id, protection_data, self.bot)
        await interaction.response.send_message(embed=embed, view=view)

    @protection.error
    async def protection_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            print(f"Erreur dans protection: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    @commands.command()
    async def addwl(self, ctx, user: discord.User):
        if ctx.author.id != self.config_ids["ISEY_ID"] and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("Désolé, vous n'avez pas l'autorisation d'utiliser cette commande.")
            return
        guild_id = str(ctx.guild.id)
        wl_data = self.collection19.find_one({"guild_id": guild_id})
        if not wl_data:
            self.collection19.insert_one({"guild_id": guild_id, "whitelist": []})
            wl_data = {"whitelist": []}
        if str(user.id) in wl_data["whitelist"]:
            await ctx.send(f"{user.name} est déjà dans la whitelist.")
        else:
            self.collection19.update_one(
                {"guild_id": guild_id},
                {"$push": {"whitelist": str(user.id)}}
            )
            await ctx.send(f"{user.name} a été ajouté à la whitelist.")

    @commands.command()
    async def removewl(self, ctx, user: discord.User):
        if ctx.author.id != self.config_ids["ISEY_ID"]:
            await ctx.send("Désolé, vous n'avez pas l'autorisation d'utiliser cette commande.")
            return
        guild_id = str(ctx.guild.id)
        wl_data = self.collection19.find_one({"guild_id": guild_id})
        if not wl_data or str(user.id) not in wl_data["whitelist"]:
            await ctx.send(f"{user.name} n'est pas dans la whitelist.")
        else:
            self.collection19.update_one(
                {"guild_id": guild_id},
                {"$pull": {"whitelist": str(user.id)}}
            )
            await ctx.send(f"{user.name} a été retiré de la whitelist.")

    @commands.command()
    async def listwl(self, ctx):
        if ctx.author.id != self.config_ids["ISEY_ID"]:
            return await ctx.send(embed=create_embed(
                "⛔ Accès refusé",
                "Vous n'avez pas l'autorisation d'utiliser cette commande.",
                discord.Color.red()
            ))
        guild_id = str(ctx.guild.id)
        wl_data = self.collection19.find_one({"guild_id": guild_id})
        if not wl_data or not wl_data.get("whitelist"):
            embed = create_embed(
                "Whitelist",
                "La whitelist de ce serveur est vide.",
                discord.Color.orange()
            )
            embed.set_footer(text="Etherya • Gestion des accès")
            return await ctx.send(embed=embed)
        whitelist_users = [f"<@{user_id}>" for user_id in wl_data["whitelist"]]
        description = "\n".join(whitelist_users)
        embed = create_embed(
            "✅ Utilisateurs Whitelistés",
            description,
            discord.Color.green()
        )
        embed.set_footer(text=f"Project : Delta • {len(whitelist_users)} utilisateur(s) whitelisté(s)")
        await ctx.send(embed=embed)

    @app_commands.command(name="set-absence", description="Configurer le salon des absences et le rôle autorisé")
    @app_commands.describe(channel="Salon de destination", role="Rôle autorisé à envoyer des absences")
    @commands.has_permissions(administrator=True)
    async def set_absence(self, interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        self.collection22.update_one(
            {"guild_id": str(interaction.guild.id)},
            {"$set": {
                "channel_id": channel.id,
                "role_id": role.id
            }},
            upsert=True
        )
        await interaction.followup.send(
            f"✅ Salon d'absence défini sur {channel.mention}, rôle autorisé : {role.mention}",
            ephemeral=True
        )

    @set_absence.error
    async def set_absence_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
        else:
            print(f"Erreur dans set_absence: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    class AbsenceModal(discord.ui.Modal, title="Déclaration d'absence"):
        def __init__(self, interaction: discord.Interaction, channel: discord.TextChannel):
            super().__init__()
            self.interaction = interaction
            self.channel = channel
            self.pseudo = TextInput(label="Pseudo", placeholder="Ton pseudo IG ou Discord", max_length=100)
            self.date = TextInput(label="Date(s)", placeholder="Ex: du 20 au 25 avril", max_length=100)
            self.raison = TextInput(label="Raison", style=discord.TextStyle.paragraph, max_length=500)
            self.add_item(self.pseudo)
            self.add_item(self.date)
            self.add_item(self.raison)

        async def on_submit(self, interaction: discord.Interaction):
            embed = create_embed("📋 Nouvelle absence déclarée", "", 0xffd700)
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
            embed.add_field(name="👤 Pseudo", value=self.pseudo.value, inline=False)
            embed.add_field(name="📅 Date", value=self.date.value, inline=False)
            embed.add_field(name="📝 Raison", value=self.raison.value, inline=False)
            embed.set_footer(text=f"ID: {interaction.user.id}")
            embed.timestamp = datetime.utcnow()
            await self.channel.send(embed=embed)
            await interaction.response.send_message("✅ Ton absence a bien été enregistrée !", ephemeral=True)

    @app_commands.command(name="absence", description="Déclarer une absence")
    async def absence(self, interaction: discord.Interaction):
        data = self.collection22.find_one({"guild_id": str(interaction.guild.id)})
        if not data:
            return await interaction.response.send_message("❌ Le système d'absence n'est pas configuré.", ephemeral=True)
        role_id = data.get("role_id")
        channel_id = data.get("channel_id")
        channel = interaction.guild.get_channel(channel_id)
        if not channel:
            return await interaction.response.send_message("❌ Le salon d'absence n'a pas été trouvé.", ephemeral=True)
        if not role_id or role_id not in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message("❌ Vous n'avez pas le rôle requis pour déclarer une absence.", ephemeral=True)
        await interaction.response.send_modal(self.AbsenceModal(interaction, channel))

    @app_commands.command(name="activate-troll", description="Active les commandes troll pour ce serveur")
    @commands.has_permissions(administrator=True)
    async def activate_troll(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        guild_name = interaction.guild.name
        self.collection27.update_one(
            {"guild_id": guild_id},
            {"$set": {"guild_name": guild_name, "troll_active": True}},
            upsert=True
        )
        await interaction.response.send_message(
            f"✅ Les commandes troll ont été **activées** sur ce serveur !", ephemeral=True
        )

    @activate_troll.error
    async def activate_troll_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("🚫 Vous devez être **administrateur** pour utiliser cette commande.", ephemeral=True)
        else:
            print(f"Erreur dans activate_troll: {error}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

    @app_commands.command(name="desactivate-troll", description="Désactive les commandes troll pour ce serveur")
    @commands.has_permissions(administrator=True)
    async def desactivate_troll(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        guild_name = interaction.guild.name
        self.collection27.update_one(
            {"guild_id": guild_id},
            {"$set": {"guild_name": guild_name, "troll_active": False}},
            upsert=True
        )
        await interaction.response.send_message(
            f"⛔ Les commandes troll ont été **désactivées** sur ce serveur !", ephemeral=True
        )

    @desactivate_troll.error
    async def desactivate_troll_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("🚫 Vous devez être **administrateur** pour utiliser cette commande.", ephemeral=True)
        else:
            print(f"Erreur dans desactivate_troll: {error}")
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

    class SensibleMenu(Select):
        def __init__(self, guild_id, sensible_data, bot_instance):
            self.guild_id = guild_id
            self.sensible_data = sensible_data
            self.bot = bot_instance

            options = [
                SelectOption(
                    label=sensitive_categories[cat][0], # Utilise le nom de la catégorie
                    description="Activer ou désactiver cette catégorie.",
                    emoji="🟢" if sensible_data.get(cat, True) else "🔴",
                    value=cat
                ) for cat in sensitive_categories.keys() # Itère sur les clés
            ]
            super().__init__(
                placeholder="🔧 Choisissez une catégorie à modifier",
                min_values=1,
                max_values=1,
                options=options
            )

        async def callback(self, interaction: discord.Interaction):
            cat = self.values[0]
            current = self.sensible_data.get(cat, True)
            new_value = not current

            try:
                self.bot.db_collections["sensible"].update_one(
                    {"guild_id": str(self.guild_id)},
                    {"$set": {
                        cat: new_value,
                        f"{cat}_updated_by": str(interaction.user.id),
                        f"{cat}_updated_at": datetime.utcnow()
                    }},
                    upsert=True
                )
            except Exception as e:
                print(f"[ERREUR] Mongo update {cat} : {e}")
                await interaction.response.send_message("Erreur BDD", ephemeral=True)
                return

            self.sensible_data[cat] = new_value
            self.sensible_data[f"{cat}_updated_by"] = interaction.user.id
            self.sensible_data[f"{cat}_updated_at"] = datetime.utcnow()

            try:
                embed = create_embed("🧠 Configuration des mots sensibles", "", discord.Color.blurple())
                for c in sensitive_categories.keys():
                    name, value = format_sensible_field(c, self.sensible_data, interaction.guild, self.bot)
                    embed.add_field(name=name, value=value, inline=False)

                embed.set_footer(text="🌺 Sélectionnez une option ci-dessous pour gérer les mots sensibles.")
                view = View()
                view.add_item(Utility.SensibleMenu(self.guild_id, self.sensible_data, self.bot))
                await interaction.response.edit_message(embed=embed, view=view)
            except Exception as e:
                print(f"[ERREUR] Update message {cat} : {e}")

    class SensibleView(View):
        def __init__(self, guild_id, sensible_data, bot_instance):
            super().__init__(timeout=None)
            self.add_item(Utility.SensibleMenu(guild_id, sensible_data, bot_instance))

    @app_commands.command(name="set-sensible", description="Configurer les catégories de mots sensibles")
    @is_admin_or_isey()
    async def set_sensible(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        try:
            sensible_data = self.collection28.find_one({"guild_id": guild_id}) or {}
        except Exception as e:
            print(f"[ERREUR] Mongo find : {e}")
            await interaction.response.send_message("Erreur lors de la lecture des données sensibles.", ephemeral=True)
            return

        for cat in sensitive_categories.keys():
            if cat not in sensible_data:
                sensible_data[cat] = True

        try:
            embed = create_embed("🧠 Configuration des mots sensibles", "", discord.Color.blurple())
            for cat in sensitive_categories.keys():
                name, value = format_sensible_field(cat, sensible_data, interaction.guild, self.bot)
                embed.add_field(name=name, value=value, inline=False)

            view = Utility.SensibleView(interaction.guild.id, sensible_data, self.bot)
            await interaction.response.send_message(embed=embed, view=view)
        except Exception as e:
            print(f"[ERREUR] Affichage de l'embed : {e}")
            await interaction.response.send_message("Erreur lors de l'affichage de la configuration.", ephemeral=True)

    @set_sensible.error
    async def set_sensible_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            print(f"Erreur dans set_sensible: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    class UrgencyClaimView(discord.ui.View):
        def __init__(self, user_id, bot_instance):
            super().__init__(timeout=None)
            self.user_id = user_id
            self.bot = bot_instance
            self.add_item(discord.ui.Button(label="🚨 Claim", style=discord.ButtonStyle.success, custom_id="claim_button"))

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            # Vérifier si l'utilisateur a le rôle STAFF_DELTA
            if self.bot.config_ids["STAFF_DELTA"] not in [r.id for r in interaction.user.roles]:
                await interaction.response.send_message("Tu n'as pas la permission de claim cette alerte.", ephemeral=True)
                return False
            return True

        @discord.ui.button(label="🚨 Claim", style=discord.ButtonStyle.success, custom_id="claim_button")
        async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.user_id not in active_alerts or active_alerts[self.user_id]['claimed']:
                await interaction.response.send_message("Cette urgence a déjà été claim.", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=False)

            active_alerts[self.user_id]['claimed'] = True

            embed = active_alerts[self.user_id]['message'].embeds[0]
            embed.set_field_at(index=4, name="📌 Statut", value=f"✅ Claimé par {interaction.user.mention}", inline=False)
            embed.color = discord.Color.green()

            await active_alerts[self.user_id]['message'].edit(
                content=f"🚨 Urgence CLAIM par {interaction.user.mention}",
                embed=embed,
                view=None
            )

            try:
                user = await interaction.client.fetch_user(self.user_id)
                embed_dm = create_embed(
                    "✅ Urgence prise en charge",
                    "Un membre de l'équipe de modération s'est occupé de ton signalement.",
                    discord.Color.green()
                )
                embed_dm.add_field(
                    name="👤 Staff en charge",
                    value=f"{interaction.user.mention} (`{interaction.user}`)",
                    inline=False
                )
                embed_dm.add_field(
                    name="📌 Prochaine étape",
                    value="Tu seras contacté si des informations supplémentaires sont nécessaires. Reste disponible.",
                    inline=False
                )
                embed_dm.set_footer(text="Merci de ta confiance. Le staff fait de son mieux pour t'aider rapidement.")
                embed_dm.timestamp = datetime.utcnow()
                await user.send(embed=embed_dm)

            except discord.Forbidden:
                pass

            await interaction.followup.send(
                f"✅ {interaction.user.mention} a claim l'urgence. L'utilisateur a été notifié en privé.",
                ephemeral=False
            )

    @app_commands.command(name="urgence", description="Signaler une urgence au staff.")
    @app_commands.describe(raison="Explique la raison de l'urgence")
    @app_commands.checks.cooldown(1, 86400, key=lambda i: i.user.id)
    async def urgence(self, interaction: discord.Interaction, raison: str):
        if await is_blacklisted(interaction.user.id):
            await interaction.response.send_message("❌ Tu es blacklist du bot. Tu ne peux pas utiliser cette commande.", ephemeral=True)
            return

        if interaction.user.id in active_alerts and not active_alerts[interaction.user.id]["claimed"]:
            await interaction.response.send_message("Tu as déjà une urgence en cours.", ephemeral=True)
            return

        target_guild = self.bot.get_guild(self.config_ids["GUILD_ID"])
        if target_guild is None:
            await interaction.response.send_message("❌ Erreur : le serveur cible est introuvable.", ephemeral=True)
            return

        channel = target_guild.get_channel(self.config_ids["CHANNEL_ID"])
        if channel is None:
            await interaction.response.send_message("❌ Erreur : le salon d'urgence est introuvable dans le serveur cible.", ephemeral=True)
            return

        timestamp = datetime.utcnow()
        invite_link = "Aucun lien disponible"
        if interaction.guild and interaction.channel.permissions_for(interaction.guild.me).create_instant_invite:
            try:
                invite = await interaction.channel.create_invite(
                    max_age=3600,
                    max_uses=1,
                    unique=True,
                    reason="Urgence signalée"
                )
                invite_link = invite.url
            except discord.Forbidden:
                invite_link = "Permissions insuffisantes pour générer une invitation"
            except Exception as e:
                invite_link = f"Erreur lors de la création du lien : {e}"

        embed = create_embed(
            "🚨 Nouvelle urgence",
            raison,
            discord.Color.red()
        )
        embed.timestamp = timestamp
        embed.set_footer(text=f"ID de l'utilisateur : {interaction.user.id}")
        embed.add_field(name="👤 Utilisateur", value=f"{interaction.user.mention} (`{interaction.user}`)", inline=True)
        embed.add_field(name="🆔 User ID", value=str(interaction.user.id), inline=True)
        embed.add_field(name="🌐 Serveur", value=interaction.guild.name if interaction.guild else "DM", inline=True)
        embed.add_field(name="📅 Date", value=f"<t:{int(timestamp.timestamp())}:F>", inline=True)
        embed.add_field(name="📌 Statut", value="⏳ En attente de claim", inline=False)
        if interaction.guild:
            embed.add_field(name="🔗 Message original", value=f"[Clique ici](https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{interaction.id})", inline=False)
        embed.add_field(name="🔗 Invitation", value=invite_link, inline=False)

        view = Utility.UrgencyClaimView(interaction.user.id, self.bot)
        message = await channel.send(
            content=f"<@&{self.config_ids['STAFF_DELTA']}> 🚨 Urgence signalée**",
            embed=embed,
            view=view
        )

        active_alerts[interaction.user.id] = {
            "message": message,
            "timestamp": timestamp,
            "claimed": False,
            "user_id": interaction.user.id,
            "username": str(interaction.user),
            "guild_name": interaction.guild.name if interaction.guild else "DM",
            "guild_id": interaction.guild.id if interaction.guild else None,
            "channel_id": channel.id,
            "reason": raison
        }
        await interaction.response.send_message("🚨 Urgence envoyée au staff du serveur principal.", ephemeral=True)

    @urgence.error
    async def urgence_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Tu dois attendre avant de signaler une nouvelle urgence. Réessaie dans {timedelta(seconds=int(error.retry_after))}.", ephemeral=True)
        else:
            print(f"Erreur dans urgence: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    class GiveawayModal(discord.ui.Modal, title="Créer un Giveaway"):
        def __init__(self, interactor):
            super().__init__()
            self.interactor = interactor
            self.duration = discord.ui.TextInput(label="Durée (ex: 10m, 2h, 1d)", required=True)
            self.winners = discord.ui.TextInput(label="Nombre de gagnants", required=True)
            self.prize = discord.ui.TextInput(label="Prix", required=True)
            self.description = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=False)
            self.add_item(self.duration)
            self.add_item(self.winners)
            self.add_item(self.prize)
            self.add_item(self.description)

        def parse_duration(self, s: str) -> int:
            unit = s[-1]
            val = int(s[:-1])
            if unit == "s": return val
            elif unit == "m": return val * 60
            elif unit == "h": return val * 3600
            elif unit == "d": return val * 86400
            else: raise ValueError("Unité invalide (utilise s, m, h ou d)")

        async def on_submit(self, interaction: discord.Interaction):
            try:
                seconds = self.parse_duration(str(self.duration))
            except:
                return await interaction.response.send_message("Durée invalide. Utilise 10m, 2h, 1d...", ephemeral=True)

            end_time = discord.utils.utcnow() + timedelta(seconds=seconds)
            giveaway_id = ''.join(str(random.randint(0, 9)) for _ in range(10))

            giveaways[giveaway_id] = {
                "participants": set(),
                "prize": str(self.prize),
                "host": self.interactor.user.id,
                "winners": int(str(self.winners)),
                "end": end_time,
                "message_id": None
            }

            extra_description = ""
            if self.description.value and self.description.value.strip():
                giveaways[giveaway_id]["description"] = self.description.value.strip()
                extra_description = f"> {self.description.value.strip()}\n\n"

            embed = create_embed(
                str(self.prize),
                (
                    f"{extra_description}"
                    f"**Ends:** <t:{int(end_time.timestamp())}:R> (<t:{int(end_time.timestamp())}:F>)\n"
                    f"**Hosted by:** {self.interactor.user.mention}\n"
                    f"**Entries:** 0\n"
                    f"**Winners:** {str(self.winners)}"
                ),
                discord.Color.blue()
            )
            embed.set_footer(text=f"ID: {giveaway_id} — Fin: {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

            view = Utility.JoinGiveawayView(giveaway_id)
            await interaction.response.send_message("Giveaway créé avec succès !", ephemeral=True)
            message = await interaction.channel.send(embed=embed, view=view)
            giveaways[giveaway_id]["message_id"] = message.id

            async def end_giveaway():
                await asyncio.sleep(seconds)
                data = giveaways.get(giveaway_id)
                if not data:
                    return

                channel = interaction.channel
                try:
                    msg = await channel.fetch_message(data["message_id"])
                except:
                    return

                if not data["participants"]:
                    await channel.send(f"🎉 Giveaway **{data['prize']}** annulé : aucun participant.")
                    await msg.edit(view=None)
                    del giveaways[giveaway_id]
                    return

                winners_list = random.sample(list(data["participants"]), min(data["winners"], len(data["participants"])))
                winner_mentions = ', '.join(f"<@{uid}>" for uid in winners_list)
                await channel.send(f"🎉 Giveaway terminé pour **{data['prize']}** ! Gagnant(s) : {winner_mentions}")

                ended_embed = create_embed(
                    data["prize"],
                    (
                        f"**Ended:** <t:{int(data['end'].timestamp())}:F>\n"
                        f"**Hosted by:** <@{data['host']}>\n"
                        f"**Entries:** {len(data['participants'])}\n"
                        f"**Winners:** {winner_mentions}"
                    ),
                    discord.Color.blue()
                )
                ended_embed.set_footer(text=f"ID: {giveaway_id} — Terminé")

                await msg.edit(embed=ended_embed, view=None)
                ended_giveaways[giveaway_id] = data
                del giveaways[giveaway_id]

            asyncio.create_task(end_giveaway())

    class JoinGiveawayView(discord.ui.View):
        def __init__(self, giveaway_id):
            super().__init__(timeout=None)
            self.giveaway_id = giveaway_id
            self.add_item(discord.ui.Button(label="🎉", style=discord.ButtonStyle.primary, custom_id="join_giveaway_btn"))

        @discord.ui.button(label="🎉", style=discord.ButtonStyle.primary, custom_id="join_giveaway_btn")
        async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
            data = giveaways.get(self.giveaway_id)
            if not data:
                return await interaction.response.send_message("Giveaway introuvable.", ephemeral=True)

            if discord.utils.utcnow() > data["end"]:
                return await interaction.response.send_message("⏰ Ce giveaway est terminé !", ephemeral=True)

            if interaction.user.id in data["participants"]:
                return await interaction.response.send_message(
                    "You have already entered this giveaway!", ephemeral=True,
                    view=Utility.LeaveGiveawayView(self.giveaway_id)
                )

            data["participants"].add(interaction.user.id)
            await self.update_embed(interaction.channel, data)
            await interaction.response.send_message("✅ Participation enregistrée !", ephemeral=True)

        async def update_embed(self, channel, data):
            try:
                msg = await channel.fetch_message(data["message_id"])
                embed = msg.embeds[0]
                lines = embed.description.split('\n')
                for i in range(len(lines)):
                    if lines[i].startswith("**Entries:**"):
                        lines[i] = f"**Entries:** {len(data['participants'])}"
                embed.description = '\n'.join(lines)
                await msg.edit(embed=embed)
            except:
                pass

    class LeaveGiveawayView(discord.ui.View):
        def __init__(self, giveaway_id):
            super().__init__(timeout=30)
            self.giveaway_id = giveaway_id
            self.add_item(discord.ui.Button(label="Leave", style=discord.ButtonStyle.danger, custom_id="leave_giveaway_btn"))

        @discord.ui.button(label="Leave", style=discord.ButtonStyle.danger, custom_id="leave_giveaway_btn")
        async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
            data = giveaways.get(self.giveaway_id)
            if data and interaction.user.id in data["participants"]:
                data["participants"].remove(interaction.user.id)
                await interaction.response.send_message("❌ Tu as quitté le giveaway.", ephemeral=True)
            else:
                await interaction.response.send_message("Tu n’étais pas inscrit !", ephemeral=True)

    @app_commands.command(name="g-create", description="Créer un giveaway")
    @commands.has_permissions(administrator=True)
    async def g_create(self, interaction: discord.Interaction):
        await interaction.response.send_modal(Utility.GiveawayModal(interaction))

    @g_create.error
    async def g_create_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Tu dois être admin pour faire ça.", ephemeral=True)
        else:
            print(f"Erreur dans g_create: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    @app_commands.command(name="g-end", description="Terminer un giveaway prématurément")
    @app_commands.describe(giveaway_id="L'ID du giveaway à terminer")
    @commands.has_permissions(administrator=True)
    async def g_end(self, interaction: discord.Interaction, giveaway_id: str):
        data = giveaways.get(giveaway_id)
        if not data:
            return await interaction.response.send_message("Giveaway introuvable ou déjà terminé.", ephemeral=True)

        channel = interaction.channel
        try:
            msg = await channel.fetch_message(data["message_id"])
        except:
            return await interaction.response.send_message("Impossible de retrouver le message du giveaway.", ephemeral=True)

        if not data["participants"]:
            await channel.send(f"🎉 Giveaway **{data['prize']}** annulé : aucun participant.")
            await msg.edit(view=None)
            del giveaways[giveaway_id]
            return await interaction.response.send_message("Giveaway terminé manuellement (aucun participant).", ephemeral=True)

        winners_list = random.sample(list(data["participants"]), min(data["winners"], len(data["participants"])))
        winner_mentions = ', '.join(f"<@{uid}>" for uid in winners_list)
        await channel.send(f"🎉 Giveaway terminé pour **{data['prize']}** ! Gagnant(s) : {winner_mentions}")

        ended_embed = create_embed(
            data["prize"],
            (
                f"**Ended (manuellement):** <t:{int(discord.utils.utcnow().timestamp())}:F>\n"
                f"**Hosted by:** <@{data['host']}>\n"
                f"**Entries:** {len(data['participants'])}\n"
                f"**Winners:** {winner_mentions}"
            ),
            discord.Color.blue()
        )
        ended_embed.set_footer(text=f"ID: {giveaway_id} — Terminé manuellement")

        await msg.edit(embed=ended_embed, view=None)

        ended_giveaways[giveaway_id] = data
        del giveaways[giveaway_id]

        await interaction.response.send_message("✅ Giveaway terminé manuellement.", ephemeral=True)

    @g_end.error
    async def g_end_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Tu dois être admin pour faire ça.", ephemeral=True)
        else:
            print(f"Erreur dans g_end: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    @app_commands.command(name="g-reroll", description="Relancer un giveaway terminé")
    @app_commands.describe(giveaway_id="L'ID du giveaway à reroll")
    @commands.has_permissions(administrator=True)
    async def g_reroll(self, interaction: discord.Interaction, giveaway_id: str):
        data = ended_giveaways.get(giveaway_id)
        if not data:
            return await interaction.response.send_message("Giveaway non trouvé ou pas encore terminé.", ephemeral=True)

        if not data["participants"]:
            return await interaction.response.send_message("Aucun participant à ce giveaway.", ephemeral=True)

        winners_list = random.sample(list(data["participants"]), min(data["winners"], len(data["participants"])))
        winner_mentions = ', '. '.join(f"<@{uid}>" for uid in winners_list)
        await interaction.response.send_message(
            f"🎉 Nouveau tirage pour **{data['prize']}** ! Gagnant(s) : {winner_mentions}"
        )

    @g_reroll.error
    async def g_reroll_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Tu dois être admin pour faire ça.", ephemeral=True)
        else:
            print(f"Erreur dans g_reroll: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    @app_commands.command(name="g-fast", description="Créer un giveaway rapide (g-fast)")
    @app_commands.describe(duration="Durée (ex: 10s, 5m)", prize="Le prix du giveaway")
    @commands.has_permissions(administrator=True)
    async def g_fast(self, interaction: discord.Interaction, duration: str, prize: str):
        def parse_duration(s):
            unit = s[-1]
            val = int(s[:-1])
            if unit == "s": return val
            elif unit == "m": return val * 60
            elif unit == "h": return val * 3600
            elif unit == "d": return val * 86400
            else: raise ValueError("Unité invalide")

        try:
            seconds = parse_duration(duration)
        except:
            return await interaction.response.send_message("Durée invalide. Utilise 10m, 2h, 1d...", ephemeral=True)

        end_time = discord.utils.utcnow() + timedelta(seconds=seconds)
        giveaway_id = ''.join(str(random.randint(0, 9)) for _ in range(10))

        data = {
            "participants": set(),
            "prize": prize,
            "host": interaction.user.id,
            "end": end_time,
            "message_id": None,
            "channel_id": interaction.channel.id
        }
        fast_giveaways[giveaway_id] = data

        embed = create_embed(
            f"🎉 Giveaway Fast - {prize}",
            (
                f"**Ends:** <t:{int(end_time.timestamp())}:R>\n"
                f"**Hosted by:** {interaction.user.mention}\n"
                f"**Entries:** 0\n"
                f"**1 Winner**"
            ),
            discord.Color.green()
        )

        view = Utility.FastGiveawayView(giveaway_id)
        msg = await interaction.channel.send(embed=embed, view=view)
        data["message_id"] = msg.id
        await interaction.response.send_message("Giveaway rapide lancé !", ephemeral=True)

        async def end_fast():
            await asyncio.sleep(seconds)
            data = fast_giveaways.get(giveaway_id)
            if not data or not data["participants"]:
                await interaction.channel.send(f"🎉 Giveaway **{data['prize']}** annulé : aucun participant.")
                return

            winner_id = random.choice(list(data["participants"]))
            winner = await self.bot.fetch_user(winner_id)

            try:
                dm = await winner.create_dm()
                dm_msg = await dm.send(
                    f"🎉 Tu as gagné **{data['prize']}** ! Réagis à ce message avec <a:fete:1375944789035319470> pour valider ta victoire."
                )
                await dm_msg.add_reaction("<a:fete:1375944789035319470>")
            except Exception:
                return await interaction.channel.send(f"❌ Impossible d'envoyer un MP à <@{winner_id}>.")

            start_time_reaction = discord.utils.utcnow()

            def check(reaction, user):
                return (
                    user.id == winner_id and
                    reaction.message.id == dm_msg.id and
                    str(reaction.emoji) == "<a:fete:1375944789035319470>"
                )

            try:
                await self.bot.wait_for('reaction_add', timeout=60, check=check)
                delay = (discord.utils.utcnow() - start_time_reaction).total_seconds()
                await interaction.channel.send(
                    f"⏱️ <@{winner_id}> a réagi en **{round(delay, 2)} secondes** pour valider sa victoire sur **{data['prize']}** !"
                )
            except asyncio.TimeoutError:
                await interaction.channel.send(
                    f"❌ <@{winner_id}> n’a pas réagi dans les 60 secondes en MP. Giveaway perdu."
                )

            del fast_giveaways[giveaway_id]

        asyncio.create_task(end_fast())

    @g_fast.error
    async def g_fast_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Tu dois être admin pour faire ça.", ephemeral=True)
        else:
            print(f"Erreur dans g_fast: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    class FastGiveawayView(discord.ui.View):
        def __init__(self, giveaway_id):
            super().__init__(timeout=None)
            self.giveaway_id = giveaway_id
            self.add_item(discord.ui.Button(label="🎉 Participer", style=discord.ButtonStyle.green, custom_id="join_fast_giveaway_btn"))

        @discord.ui.button(label="🎉 Participer", style=discord.ButtonStyle.green, custom_id="join_fast_giveaway_btn")
        async def join_fast(self, interaction: discord.Interaction, button: discord.ui.Button):
            data = fast_giveaways.get(self.giveaway_id)
            if not data:
                return await interaction.response.send_message("Giveaway introuvable.", ephemeral=True)
            if discord.utils.utcnow() > data["end"]:
                return await interaction.response.send_message("⏰ Ce giveaway est terminé !", ephemeral=True)
            if interaction.user.id in data["participants"]:
                return await interaction.response.send_message("Tu es déjà inscrit !", ephemeral=True)

            data["participants"].add(interaction.user.id)
            await interaction.response.send_message("✅ Participation enregistrée !", ephemeral=True)

    @app_commands.command(name="etherya", description="Obtiens le lien du serveur Etherya !")
    async def etherya(self, interaction: discord.Interaction):
        message = (
            "🌟 **[𝑺ץ] 𝑬𝒕𝒉𝒆𝒓𝒚𝒂 !** 🌟\n\n"
            "🍣 ・ Un serveur **Communautaire**\n"
            "🌸 ・ Des membres sympas et qui **sont actifs** !\n"
            "🌋 ・ Des rôles **exclusifs** avec une **boutique** !\n"
            "🎐 ・ **Safe place** & **Un Système Économique développé** !\n"
            "☕ ・ Divers **Salons** pour un divertissement optimal.\n"
            "☁️ ・ Un staff sympa, à l'écoute et qui **recrute** !\n"
            "🔥 ・ Pas convaincu ? Rejoins-nous et vois par toi-même le potentiel de notre serveur !\n\n"
            "🎫 **[Accès direct au serveur Etherya !](https://discord.gg/2CXDSSRTYz) **\n\n"
            "Rejoins-nous et amuse-toi ! 🎉"
        )
        await interaction.response.send_message(message)

    class InfoView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(Utility.PointSystemButton())
            self.add_item(Utility.PriceServiceButton())

    class PointSystemButton(discord.ui.Button):
        def __init__(self):
            super().__init__(
                label="Système de Gain de points",
                style=discord.ButtonStyle.primary,
                custom_id="pointsystem_btn"
            )

        async def callback(self, interaction: discord.Interaction):
            embed = create_embed("", "", discord.Color(0x1ABC9C))
            embed.set_image(url="IMAGES EVENT/1.jpg") # Chemin corrigé

            view = discord.ui.View(timeout=None)
            view.add_item(Utility.ImageButton("Project : Delta", "IMAGES EVENT/2.jpg", "project_image_btn")) # Chemin corrigé
            view.add_item(Utility.ImageButton("Annonce", "IMAGES EVENT/3.jpg", "annonce_image_btn")) # Chemin corrigé

            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    class PriceServiceButton(discord.ui.Button):
        def __init__(self):
            super().__init__(
                label="Prix des Services",
                style=discord.ButtonStyle.secondary,
                custom_id="price_service_btn"
            )

        async def callback(self, interaction: discord.Interaction):
            embed = create_embed(
                "💰 Prix des Services",
                "Les prix varient selon le service demandé et sa complexité.",
                discord.Color(0x3498DB)
            )

            view = discord.ui.View(timeout=None)
            view.add_item(Utility.ImageButton("Bot Discord", "IMAGES EVENT/4.jpg", "img_botdiscord")) # Chemin corrigé
            view.add_item(Utility.ImageButton("Site Web", "IMAGES EVENT/5.jpg", "img_siteweb")) # Chemin corrigé
            view.add_item(Utility.ImageButton("Serveur Discord", "IMAGES EVENT/6.jpg", "img_servdiscord")) # Chemin corrigé
            view.add_item(Utility.ImageButton("Prestations Annexes", "IMAGES EVENT/7.jpg", "img_annexe")) # Chemin corrigé

            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    class ImageButton(discord.ui.Button):
        def __init__(self, label, image_url, custom_id):
            super().__init__(label=label, style=discord.ButtonStyle.success, custom_id=custom_id)
            self.image_url = image_url

        async def callback(self, interaction: discord.Interaction):
            embed = create_embed("", "", discord.Color(0x2C3E50))
            embed.set_image(url=self.image_url)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command()
    async def info(self, ctx):
        if ctx.author.id != self.config_ids["ISEY_ID"]:
            return await ctx.send("❌ Tu n'es pas autorisé à utiliser cette commande.")

        embed = create_embed(
            "**ÉVÉNEMENT SPÉCIAL — LANCEMENT OFFICIEL DE PROJECT : DELTA**",
            (
                "> <:dev_white:1376909968141451274>  **Un bot complet pour gérer, protéger et animer votre serveur Discord.**\n"
                "> <a:fete:1375944789035319470>  Simple, puissant, gratuit (Premium offert pendant la phase de test) !\n\n"

                "## <:bot:1377223809832058971>・**Project : Delta – Le Bot**\n\n"
                "<:shield:1377224699955773523>  Anti-raid puissant – Ne laissez aucune attaque passer.\n"
                "<:Vocal:1361766779143061767>  Détection automatique de mots sensibles – Modération intelligente.\n"
                "<:tools:1377227900037632060>  Outils de gestion simples et efficaces – Kick, ban, clear, logs, et plus.\n"
                "<:member:1377228477131919370>  Giveaways & commandes fun – Pour animer votre communauté avec style.\n\n"

                "<:files:1377229165572395079>  **Fonctionnalités à venir :**\n"
                "<:uoad:1377229381784698932>  *Sauvegarde de serveur.*\n"
                "<:ticket:1377229577880997918> *Tickets.*\n"
                "<:delertle:1377229695086628884> *Logs.*\n"
                "<a:recaptcha:1377230186545942609> *Captcha*\n\n"

                "<a:fete:1377230403114635415> **Offre actuelle** : Tous les serveurs qui ajoutent le bot ont un **statut Premium GRATUIT** pendant la phase de test !\n\n"
                "<:emoji_36:136199234836365