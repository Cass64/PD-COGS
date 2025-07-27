import discord
from discord.ext import commands
from discord import app_commands, Embed, ButtonStyle, ui
from discord.ui import Button, View, Select, Modal, TextInput
from datetime import datetime, timedelta, timezone
import asyncio
import re
import os
import pytz

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

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collection = bot.db_collections["setup"]
        self.collection4 = bot.db_collections["protection"]
        self.collection19 = bot.db_collections["wl"]
        self.collection20 = bot.db_collections["suggestions"]
        self.collection21 = bot.db_collections["presentation"]
        self.collection22 = bot.db_collections["absence"]
        self.collection27 = bot.db_collections["guild_troll"]
        self.collection28 = bot.db_collections["sensible"]
        self.collection31 = bot.db_collections["delta_event"]
        self.collection32 = bot.db_collections["delta_statut"]
        self.collection33 = bot.db_collections["ds_stats"]
        self.config_ids = bot.config_ids

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = None):
        if amount is None:
            await ctx.send("Merci de préciser un chiffre entre 2 et 100.")
            return
        if amount < 2 or amount > 100:
            await ctx.send("Veuillez spécifier un nombre entre 2 et 100.")
            return

        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f'{len(deleted)} messages supprimés.', delete_after=5)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, user: discord.Member = None, role: discord.Role = None):
        if user is None or role is None:
            await ctx.send("Erreur : veuillez suivre ce format : `+addrole @user @rôle`")
            return
        try:
            await user.add_roles(role)
            await ctx.send(f"{user.mention} a maintenant le rôle {role.name} !")
        except discord.Forbidden:
            await ctx.send("Je n'ai pas les permissions nécessaires pour attribuer ce rôle.")
        except discord.HTTPException as e:
            await ctx.send(f"Une erreur est survenue : {e}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def delrole(self, ctx, user: discord.Member = None, role: discord.Role = None):
        if user is None or role is None:
            await ctx.send("Erreur : veuillez suivre ce format : `+delrole @user @rôle`")
            return
        try:
            await user.remove_roles(role)
            await ctx.send(f"{user.mention} n'a plus le rôle {role.name} !")
        except discord.Forbidden:
            await ctx.send("Je n'ai pas les permissions nécessaires pour retirer ce rôle.")
        except discord.HTTPException as e:
            await ctx.send(f"Une erreur est survenue : {e}")

    @commands.command()
    @commands.has_permissions(administrator=True) # Utilisation de la permission Discord
    async def massrole(self, ctx, action: str = None, role: discord.Role = None):
        if action is None or role is None:
            return await ctx.send("Erreur : tu dois spécifier l'action ('add' ou 'remove') et le rôle. Exemple : `+massrole add @role` ou `+massrole remove @role`.")

        if action not in ['add', 'remove']:
            return await ctx.send("Erreur : l'action doit être 'add' ou 'remove'.")

        for member in ctx.guild.members:
            if not member.bot:
                try:
                    if action == 'add':
                        await member.add_roles(role)
                    elif action == 'remove':
                        await member.remove_roles(role)
                    print(f"Le rôle a été {action}é pour {member.name}")
                except discord.DiscordException as e:
                    print(f"Erreur avec {member.name}: {e}")

        await ctx.send(f"Le rôle '{role.name}' a été {action} à tous les membres humains du serveur.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx):
        if isinstance(ctx.channel, discord.TextChannel):
            channel = ctx.channel
            overwrites = channel.overwrites
            channel_name = channel.name
            category = channel.category
            position = channel.position
            guild = channel.guild

            try:
                await channel.delete()
                new_channel = await guild.create_text_channel(
                    name=channel_name,
                    overwrites=overwrites,
                    category=category
                )
                await new_channel.edit(position=position)
                await new_channel.send(
                    f"💥 {ctx.author.mention} a **nuké** ce salon. Il a été recréé avec succès."
                )
            except Exception as e:
                await ctx.send(f"Une erreur est survenue lors de la recréation du salon : {e}")
        else:
            await ctx.send("Cette commande doit être utilisée dans un salon texte.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def listban(self, ctx):
        bans = [ban async for ban in ctx.guild.bans()]

        if not bans:
            embed = create_embed(
                "📜 Liste des bannis",
                "✅ Aucun utilisateur n'est actuellement banni du serveur.",
                discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)
            return await ctx.send(embed=embed)

        pages = []
        content = ""

        for i, ban in enumerate(bans, 1):
            user = ban.user
            reason = ban.reason or "Aucune raison spécifiée"
            entry = f"🔹 **{user.name}#{user.discriminator}**\n📝 *{reason}*\n\n"

            if len(content + entry) > 1000:
                pages.append(content)
                content = ""
            content += entry

        if content:
            pages.append(content)

        for idx, page in enumerate(pages, 1):
            embed = create_embed(
                f"📜 Liste des bannis (Page {idx}/{len(pages)})",
                page,
                discord.Color.red()
            )
            embed.set_footer(text=f"Total : {len(bans)} utilisateur(s) banni(s)")
            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon.url)
            await ctx.send(embed=embed)

    @commands.command(name="unbanall")
    @commands.has_permissions(administrator=True)
    async def unbanall(self, ctx):
        async for ban_entry in ctx.guild.bans():
            await ctx.guild.unban(ban_entry.user)
        await ctx.send("✅ Tous les utilisateurs bannis ont été débannis !")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def alladmin(self, ctx):
        admins = [member for member in ctx.guild.members if member.guild_permissions.administrator]

        if not admins:
            embed = create_embed(
                "❌ Aucun administrateur trouvé",
                "Il semble que personne n'ait les permissions d'administrateur sur ce serveur.",
                discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        embed = create_embed(
            "📜 Liste des administrateurs",
            f"Voici les {len(admins)} administrateurs du serveur **{ctx.guild.name}** :",
            discord.Color.blue()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text=f"Commande demandée par {ctx.author.name}", icon_url=ctx.author.avatar.url)

        for admin in admins:
            embed.add_field(name=f"👤 {admin.name}#{admin.discriminator}", value=f"ID : `{admin.id}`", inline=False)

        await ctx.send(embed=embed)

    class EmbedTitleModal(discord.ui.Modal):
        def __init__(self, view: 'EmbedBuilderView'):
            super().__init__(title="Modifier le Titre")
            self.view = view
            self.title_input = discord.ui.TextInput(label="Nouveau Titre", required=True)
            self.add_item(self.title_input)

        async def on_submit(self, interaction: discord.Interaction):
            self.view.embed.title = self.title_input.value
            if self.view.message:
                await self.view.message.edit(embed=self.view.embed, view=self.view)
            else:
                await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

    class EmbedDescriptionModal(discord.ui.Modal):
        def __init__(self, view: 'EmbedBuilderView'):
            super().__init__(title="Modifier la description")
            self.view = view
            self.description = discord.ui.TextInput(label="Nouvelle description", style=discord.TextStyle.paragraph, max_length=4000)
            self.add_item(self.description)

        async def on_submit(self, interaction: discord.Interaction):
            self.view.embed.description = self.description.value
            if self.view.message:
                await self.view.message.edit(embed=self.view.embed, view=self.view)
            else:
                await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

    class EmbedImageModal(discord.ui.Modal):
        def __init__(self, view: 'EmbedBuilderView'):
            super().__init__(title="Ajouter une image")
            self.view = view
            self.image_input = discord.ui.TextInput(label="URL de l'image", required=True)
            self.add_item(self.image_input)

        async def on_submit(self, interaction: discord.Interaction):
            if is_valid_url(self.image_input.value):
                self.view.embed.set_image(url=self.image_input.value)
                await self.view.message.edit(embed=self.view.embed, view=self.view)
            else:
                await interaction.response.send_message("❌ URL invalide.", ephemeral=True)

    class EmbedSecondImageModal(discord.ui.Modal):
        def __init__(self, view: 'EmbedBuilderView'):
            super().__init__(title="Ajouter une 2ème image")
            self.view = view
            self.second_image_input = discord.ui.TextInput(label="URL de la 2ème image", required=True)
            self.add_item(self.second_image_input)

        async def on_submit(self, interaction: discord.Interaction):
            if is_valid_url(self.second_image_input.value):
                self.view.second_image_url = self.second_image_input.value
            else:
                await interaction.response.send_message("❌ URL invalide.", ephemeral=True)

    class EmbedBuilderView(discord.ui.View):
        def __init__(self, author: discord.User, channel: discord.TextChannel):
            super().__init__(timeout=180)
            self.author = author
            self.channel = channel
            self.embed = discord.Embed(title="Titre", description="Description", color=discord.Color.blue())
            self.embed.set_thumbnail(url=THUMBNAIL_URL)
            self.second_image_url = None
            self.message = None

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.author:
                await interaction.response.send_message("❌ Vous ne pouvez pas modifier cet embed.", ephemeral=True)
                return False
            return True

        @discord.ui.button(label="Modifier le titre", style=discord.ButtonStyle.primary)
        async def edit_title(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_modal(Admin.EmbedTitleModal(self))

        @discord.ui.button(label="Modifier la description", style=discord.ButtonStyle.primary)
        async def edit_description(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_modal(Admin.EmbedDescriptionModal(self))

        @discord.ui.button(label="Changer la couleur", style=discord.ButtonStyle.primary)
        async def edit_color(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.embed.color = discord.Color.random()
            if self.message:
                await self.message.edit(embed=self.embed, view=self)
            else:
                await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

        @discord.ui.button(label="Ajouter une image", style=discord.ButtonStyle.secondary)
        async def add_image(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_modal(Admin.EmbedImageModal(self))

        @discord.ui.button(label="Ajouter 2ème image", style=discord.ButtonStyle.secondary)
        async def add_second_image(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_modal(Admin.EmbedSecondImageModal(self))

        @discord.ui.button(label="Envoyer", style=discord.ButtonStyle.success)
        async def send_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
            embeds = [self.embed]
            if self.second_image_url:
                second_embed = discord.Embed(color=self.embed.color)
                second_embed.set_image(url=self.second_image_url)
                embeds.append(second_embed)

            await self.channel.send(embeds=embeds)
            await interaction.response.send_message("✅ Embed envoyé !", ephemeral=True)

    @app_commands.command(name="embed", description="Créer un embed personnalisé")
    @app_commands.checks.has_permissions(administrator=True)
    async def embed_builder(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        view = self.EmbedBuilderView(interaction.user, interaction.channel)
        response = await interaction.followup.send(embed=view.embed, view=view, ephemeral=True)
        view.message = response

    @embed_builder.error
    async def embed_builder_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        else:
            print(f"Erreur dans embed_builder: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔒 Salon verrouillé. Seuls les rôles autorisés peuvent parler.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unlock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔓 Salon déverrouillé. Tout le monde peut parler à nouveau.")

    class FeedbackModal(discord.ui.Modal, title="Envoyer un feedback"):
        def __init__(self, bot_instance):
            super().__init__()
            self.bot = bot_instance

        feedback_type = discord.ui.TextInput(
            label="Type (Report ou Suggestion)",
            placeholder="Ex: Report",
            max_length=20
        )

        description = discord.ui.TextInput(
            label="Description",
            placeholder="Décris ton idée ou ton problème ici...",
            style=discord.TextStyle.paragraph,
            max_length=1000
        )

        async def on_submit(self, interaction: discord.Interaction):
            channel = self.bot.get_channel(self.bot.config_ids["SALON_REPORT_ID"])
            role_mention = f"<@&{self.bot.config_ids['ROLE_REPORT_ID']}>"

            await channel.send(content=role_mention)

            embed = create_embed(
                "📝 Nouveau Feedback Reçu",
                "",
                discord.Color.blurple()
            )
            embed.add_field(name="🔖 Type", value=self.feedback_type.value, inline=False)
            embed.add_field(name="🧾 Description", value=self.description.value, inline=False)
            embed.add_field(name="👤 Utilisateur", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
            embed.add_field(name="🌐 Serveur", value=f"{interaction.guild.name} (`{interaction.guild.id}`)", inline=False)

            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.set_footer(text="Feedback envoyé le", icon_url=interaction.user.display_avatar.url)
            embed.timestamp = datetime.utcnow()

            await channel.send(embed=embed)
            await interaction.response.send_message("✅ Ton feedback a bien été envoyé ! Merci !", ephemeral=True)

    @app_commands.command(name="feedback", description="Envoyer un report ou une suggestion")
    async def feedback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.FeedbackModal(self.bot))

async def setup(bot):
    await bot.add_cog(Admin(bot))

