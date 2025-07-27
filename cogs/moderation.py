import discord
from discord.ext import commands
from discord import app_commands, Embed
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

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collection7 = bot.db_collections["sanction"] # Collection pour les sanctions
        self.collection24 = bot.db_collections["delta_warn"] # Collection pour les warns Delta
        self.collection25 = bot.db_collections["delta_bl"] # Collection pour les blacklist Delta
        self.config_ids = bot.config_ids

    @app_commands.command(
        name="mute",
        description="Mute temporairement un membre (timeout) avec une durée spécifiée."
    )
    @app_commands.describe(
        member="Le membre à mute",
        duration_with_unit="La durée (ex: 10m, 2h, 1d)",
        reason="La raison du mute"
    )
    @commands.has_permissions(moderate_members=True)
    async def mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration_with_unit: str,
        reason: str = "Aucune raison spécifiée"
    ):
        ctx = await self.bot.get_context(interaction) # Obtenir un contexte pour les fonctions utilitaires

        if interaction.user == member:
            return await interaction.response.send_message("🚫 Vous ne pouvez pas vous mute vous-même.", ephemeral=True)

        if is_higher_or_equal(ctx, member):
            return await interaction.response.send_message("🚫 Vous ne pouvez pas sanctionner quelqu'un de votre niveau ou supérieur.", ephemeral=True)

        if member.timed_out_until and member.timed_out_until > datetime.utcnow().replace(tzinfo=timezone.utc):
            timeout_end = member.timed_out_until.strftime('%d/%m/%Y à %H:%M:%S')
            return await interaction.response.send_message(f"❌ {member.mention} est déjà en timeout jusqu'au {timeout_end} UTC.", ephemeral=True)

        time_units = {"m": "minutes", "h": "heures", "d": "jours"}
        try:
            duration = int(duration_with_unit[:-1])
            unit = duration_with_unit[-1].lower()
            if unit not in time_units:
                raise ValueError
        except ValueError:
            return await interaction.response.send_message("❌ Format invalide ! Utilisez un nombre suivi de `m` (minutes), `h` (heures) ou `j` (jours).", ephemeral=True)

        time_deltas = {"m": timedelta(minutes=duration), "h": timedelta(hours=duration), "d": timedelta(days=duration)}
        duration_time = time_deltas[unit]
        duration_str = f"{duration} {time_units[unit]}"

        try:
            await member.timeout(duration_time, reason=reason)

            embed = create_embed(
                "⏳ Mute",
                f"{member.mention} a été muté pour {duration_str}.",
                discord.Color.blue(),
                footer_text=f"Action effectuée par {interaction.user.name}"
            )
            embed.add_field(name="👤 Membre sanctionné", value=member.mention, inline=True)
            embed.add_field(name="⚖️ Sanction", value="Mute", inline=True)
            embed.add_field(name="📜 Raison", value=reason, inline=False)
            embed.add_field(name="⏳ Durée", value=duration_str, inline=True)
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.timestamp = datetime.utcnow()

            await interaction.response.send_message(embed=embed)
            await send_dm(member, "Mute", reason, duration_str)

            sanction_data = {
                "guild_id": str(interaction.guild.id),
                "user_id": str(member.id),
                "action": "Mute",
                "reason": reason,
                "duration": duration_str,
                "timestamp": datetime.utcnow()
            }
            self.collection7.insert_one(sanction_data)

        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas la permission de mute ce membre. Vérifiez les permissions du bot.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ Une erreur s'est produite lors de l'application du mute : {e}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Une erreur inattendue s'est produite : {str(e)}", ephemeral=True)

    @mute.error
    async def mute_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Vous n'avez pas la permission de mute des membres.", ephemeral=True)
        else:
            print(f"Erreur dans mute: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    @app_commands.command(
        name="ban",
        description="Bannit un membre du serveur avec une raison optionnelle."
    )
    @app_commands.describe(
        member="Le membre à bannir",
        reason="La raison du bannissement"
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison spécifiée"):
        ctx = await self.bot.get_context(interaction)

        if interaction.user == member:
            return await interaction.response.send_message("🚫 Vous ne pouvez pas vous bannir vous-même.", ephemeral=True)

        if is_higher_or_equal(ctx, member):
            return await interaction.response.send_message("🚫 Vous ne pouvez pas sanctionner quelqu'un de votre niveau ou supérieur.", ephemeral=True)

        try:
            await member.ban(reason=reason)
            embed = create_embed(
                "🔨 Ban",
                f"{member.mention} a été banni.",
                discord.Color.red(),
                footer_text=f"Action effectuée par {interaction.user.name}"
            )
            embed.add_field(name="👤 Membre sanctionné", value=member.mention, inline=True)
            embed.add_field(name="⚖️ Sanction", value="Ban", inline=True)
            embed.add_field(name="📜 Raison", value=reason, inline=False)
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.timestamp = datetime.utcnow()

            await interaction.response.send_message(embed=embed)
            await send_log(ctx, member, "Ban", reason)
            await send_dm(member, "Ban", reason)

            add_sanction(interaction.guild.id, member.id, "Ban", reason)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas la permission de bannir ce membre. Vérifiez les permissions du bot.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Une erreur s'est produite : {str(e)}", ephemeral=True)

    @ban.error
    async def ban_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Vous n'avez pas la permission de bannir des membres.", ephemeral=True)
        else:
            print(f"Erreur dans ban: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    @app_commands.command(
        name="unban",
        description="Débannit un utilisateur du serveur à partir de son ID."
    )
    @app_commands.describe(
        user_id="L'ID de l'utilisateur à débannir"
    )
    @commands.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            embed = create_embed(
                "🔓 Unban",
                f"{user.mention} a été débanni.",
                discord.Color.green(),
                footer_text=f"Action effectuée par {interaction.user.name}"
            )
            embed.add_field(name="👤 Utilisateur débanni", value=user.mention, inline=True)
            embed.add_field(name="⚖️ Sanction", value="Unban", inline=True)
            embed.add_field(name="📜 Raison", value="Réintégration", inline=False)
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.timestamp = datetime.utcnow()

            await interaction.response.send_message(embed=embed)
            ctx = await self.bot.get_context(interaction)
            await send_log(ctx, user, "Unban", "Réintégration")
            await send_dm(user, "Unban", "Réintégration")
        except discord.NotFound:
            await interaction.response.send_message("❌ Aucun utilisateur trouvé avec cet ID.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas les permissions nécessaires pour débannir cet utilisateur.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Une erreur s'est produite : {str(e)}", ephemeral=True)

    @unban.error
    async def unban_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Vous n'avez pas la permission de débannir des membres.", ephemeral=True)
        else:
            print(f"Erreur dans unban: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    @app_commands.command(
        name="kick",
        description="Expulse un membre du serveur avec une raison optionnelle."
    )
    @app_commands.describe(
        member="Le membre à expulser",
        reason="La raison de l'expulsion"
    )
    @commands.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison spécifiée"):
        ctx = await self.bot.get_context(interaction)

        if interaction.user == member:
            return await interaction.response.send_message("🚫 Vous ne pouvez pas vous expulser vous-même.", ephemeral=True)
        if is_higher_or_equal(ctx, member):
            return await interaction.response.send_message("🚫 Vous ne pouvez pas sanctionner quelqu'un de votre niveau ou supérieur.", ephemeral=True)

        try:
            await member.kick(reason=reason)
            embed = create_embed(
                "👢 Kick",
                f"{member.mention} a été expulsé.",
                discord.Color.orange(),
                footer_text=f"Action effectuée par {interaction.user.name}"
            )
            embed.add_field(name="👤 Membre expulsé", value=member.mention, inline=True)
            embed.add_field(name="⚖️ Sanction", value="Kick", inline=True)
            embed.add_field(name="📜 Raison", value=reason, inline=False)
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.timestamp = datetime.utcnow()

            await interaction.response.send_message(embed=embed)
            await send_log(ctx, member, "Kick", reason)
            await send_dm(member, "Kick", reason)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas la permission d'expulser ce membre. Vérifiez les permissions du bot.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Une erreur s'est produite : {str(e)}", ephemeral=True)

    @kick.error
    async def kick_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Vous n'avez pas la permission d'expulser des membres.", ephemeral=True)
        else:
            print(f"Erreur dans kick: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    @app_commands.command(
        name="unmute",
        description="Retire le mute d'un membre (timeout)."
    )
    @app_commands.describe(
        member="Le membre à démuter"
    )
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        ctx = await self.bot.get_context(interaction)

        try:
            await member.timeout(None)
            embed = create_embed(
                "🔊 Unmute",
                f"{member.mention} a été démuté.",
                discord.Color.green(),
                footer_text=f"Action effectuée par {interaction.user.name}"
            )
            embed.add_field(name="👤 Membre démuté", value=member.mention, inline=True)
            embed.add_field(name="⚖️ Sanction", value="Unmute", inline=True)
            embed.add_field(name="📜 Raison", value="Fin du mute", inline=False)
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.timestamp = datetime.utcnow()

            await interaction.response.send_message(embed=embed)
            await send_log(ctx, member, "Unmute", "Fin du mute")
            await send_dm(member, "Unmute", "Fin du mute")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas la permission de démuter ce membre. Vérifiez les permissions du bot.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Une erreur s'est produite : {str(e)}", ephemeral=True)

    @unmute.error
    async def unmute_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Vous n'avez pas la permission de démuter des membres.", ephemeral=True)
        else:
            print(f"Erreur dans unmute: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    @app_commands.command(
        name="warn",
        description="Avertit un membre avec une raison optionnelle."
    )
    @app_commands.describe(
        member="Le membre à avertir",
        reason="La raison de l'avertissement"
    )
    @commands.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison spécifiée"):
        ctx = await self.bot.get_context(interaction)

        if interaction.user == member:
            return await interaction.response.send_message("🚫 Vous ne pouvez pas vous avertir vous-même.", ephemeral=True)

        if is_higher_or_equal(ctx, member):
            return await interaction.response.send_message("🚫 Vous ne pouvez pas avertir quelqu'un de votre niveau ou supérieur.", ephemeral=True)

        try:
            sanction_data = {
                "guild_id": str(interaction.guild.id),
                "user_id": str(member.id),
                "action": "Warn",
                "reason": reason,
                "timestamp": datetime.utcnow()
            }
            self.collection7.insert_one(sanction_data)

            embed = create_embed(
                "⚠️ Avertissement donné",
                f"{member.mention} a reçu un avertissement pour la raison suivante :\n{reason}",
                discord.Color.orange(),
                footer_text=f"Action effectuée par {interaction.user.name}"
            )
            embed.add_field(name="👤 Membre averti", value=member.mention, inline=True)
            embed.add_field(name="⚖️ Sanction", value="Avertissement", inline=True)
            embed.add_field(name="📜 Raison", value=reason, inline=False)
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.timestamp = datetime.utcnow()

            await interaction.response.send_message(embed=embed)
            await send_log(ctx, member, "Warn", reason)
            await send_dm(member, "Avertissement", reason)

        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande warn : {e}")
            await interaction.response.send_message(f"❌ Une erreur s'est produite lors de l'exécution de la commande. Détails : {str(e)}", ephemeral=True)

    @warn.error
    async def warn_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Vous n'avez pas la permission de donner des avertissements.", ephemeral=True)
        else:
            print(f"Erreur dans warn: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    @app_commands.command(
        name="warnlist",
        description="Affiche la liste des avertissements d’un membre."
    )
    @app_commands.describe(
        member="Le membre dont vous voulez voir les avertissements"
    )
    async def warnlist(self, interaction: discord.Interaction, member: discord.Member):
        sanctions = self.collection7.find({
            "guild_id": str(interaction.guild.id),
            "user_id": str(member.id),
            "action": "Warn"
        })

        count = self.collection7.count_documents({
            "guild_id": str(interaction.guild.id),
            "user_id": str(member.id),
            "action": "Warn"
        })

        if count == 0:
            return await interaction.response.send_message(f"✅ {member.mention} n'a aucun avertissement.", ephemeral=True)

        embed = create_embed(f"Avertissements de {member.display_name}", "", discord.Color.orange())
        for sanction in sanctions:
            date = sanction["timestamp"].strftime("%d/%m/%Y à %Hh%M")
            embed.add_field(name=f"Le {date}", value=sanction["reason"], inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="unwarn",
        description="Supprime un avertissement d’un membre à partir de son index dans la warnlist."
    )
    @app_commands.describe(
        member="Le membre dont vous voulez retirer un avertissement",
        index="L'index de l'avertissement à supprimer (commence à 1)"
    )
    @commands.has_permissions(moderate_members=True)
    async def unwarn(self, interaction: discord.Interaction, member: discord.Member, index: int):
        ctx = await self.bot.get_context(interaction)

        warnings = list(self.collection7.find({
            "guild_id": str(interaction.guild.id),
            "user_id": str(member.id),
            "action": "Warn"
        }).sort("timestamp", 1))

        if len(warnings) == 0:
            return await interaction.response.send_message(f"✅ {member.mention} n'a aucun avertissement.", ephemeral=True)

        if index < 1 or index > len(warnings):
            return await interaction.response.send_message(f"❌ Index invalide. Ce membre a {len(warnings)} avertissement(s).", ephemeral=True)

        try:
            to_delete = warnings[index - 1]
            self.collection7.delete_one({"_id": to_delete["_id"]})

            embed = create_embed(
                "✅ Avertissement retiré",
                f"L’avertissement n°{index} de {member.mention} a été supprimé.",
                discord.Color.green(),
                footer_text=f"Action effectuée par {interaction.user.name}"
            )
            embed.add_field(name="👤 Membre", value=member.mention, inline=True)
            embed.add_field(name="⚖️ Action", value="Unwarn", inline=True)
            embed.add_field(name="📜 Raison", value=to_delete["reason"], inline=False)
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.timestamp = datetime.utcnow()

            await interaction.response.send_message(embed=embed)
            await send_log(ctx, member, "Unwarn", to_delete["reason"])
            await send_dm(member, "Unwarn", f"Ton avertissement datant du {to_delete['timestamp'].strftime('%d/%m/%Y à %Hh%M')} a été retiré.")

        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande unwarn : {e}")
            await interaction.response.send_message(f"❌ Une erreur s'est produite lors de la suppression de l'avertissement. Détails : {str(e)}", ephemeral=True)

    @unwarn.error
    async def unwarn_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Vous n'avez pas la permission de retirer des avertissements.", ephemeral=True)
        else:
            print(f"Erreur dans unwarn: {error}")
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)

    # Staff Project : Delta Commands
    def is_staff(self, ctx):
        guild = self.bot.get_guild(self.config_ids["PROJECT_DELTA"])
        if not guild:
            return False
        member = guild.get_member(ctx.author.id)
        if not member:
            return False
        return any(role.id == self.config_ids["STAFF_DELTA"] for role in member.roles)

    async def is_target_protected(self, user_id: int):
        guild = self.bot.get_guild(self.config_ids["PROJECT_DELTA"])
        if not guild:
            return False
        member = guild.get_member(user_id)
        if not member:
            return False
        return any(role.permissions.administrator for role in member.roles)

    @commands.hybrid_command(name="delta-warn", description="Avertir un utilisateur")
    async def delta_warn(self, ctx, member: discord.Member, *, reason: str):
        if not self.is_staff(ctx):
            return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

        if await self.is_target_protected(member.id):
            return await ctx.reply("Tu ne peux pas warn cet utilisateur.")

        self.collection24.insert_one({
            "user_id": str(member.id),
            "moderator_id": str(ctx.author.id),
            "reason": reason,
            "timestamp": datetime.utcnow()
        })

        try:
            await member.send(f"🚨 Tu as reçu un **avertissement** sur **Project : Delta**.\n**Raison :** `{reason}`")
        except:
            pass

        embed = create_embed(
            "📌 Avertissement appliqué",
            f"{member.mention} a été averti.",
            discord.Color.orange()
        )
        embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=True)
        embed.add_field(name="💬 Raison", value=reason, inline=False)
        embed.timestamp = datetime.utcnow()
        await ctx.reply(embed=embed)

        log_channel = self.bot.get_channel(self.config_ids["WARN_LOG_CHANNEL"])
        if log_channel:
            await log_channel.send(embed=embed)

    @commands.hybrid_command(name="delta-unwarn", description="Retirer un avertissement")
    async def delta_unwarn(self, ctx, member: discord.Member, *, reason: str):
        if not self.is_staff(ctx):
            return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

        warn = self.collection24.find_one_and_delete({"user_id": str(member.id)})
        if warn:
            try:
                await member.send(f"✅ Ton **avertissement** sur **Project : Delta** a été retiré.\n**Raison :** `{reason}`")
            except:
                pass

            embed = create_embed(
                "✅ Avertissement retiré",
                f"{member.mention} n'est plus averti.",
                discord.Color.green()
            )
            embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=True)
            embed.add_field(name="💬 Raison", value=reason, inline=False)
            embed.timestamp = datetime.utcnow()
            await ctx.reply(embed=embed)

            log_channel = self.bot.get_channel(self.config_ids["UNWARN_LOG_CHANNEL"])
            if log_channel:
                await log_channel.send(embed=embed)
        else:
            await ctx.reply(f"{member.mention} n'a pas de warn.")

    @commands.hybrid_command(name="delta-blacklist", description="Blacklist un utilisateur")
    async def delta_blacklist(self, ctx, member: discord.Member, *, reason: str):
        if not self.is_staff(ctx):
            return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

        if await self.is_target_protected(member.id):
            return await ctx.reply("Tu ne peux pas blacklist cet utilisateur.")

        self.collection25.update_one(
            {"user_id": str(member.id)},
            {"$set": {
                "reason": reason,
                "timestamp": datetime.utcnow()
            }},
            upsert=True
        )

        try:
            await member.send(f"⛔ Tu as été **blacklist** du bot **Project : Delta**.\n**Raison :** `{reason}`")
        except:
            pass

        embed = create_embed(
            "⛔ Utilisateur blacklist",
            f"{member.mention} a été ajouté à la blacklist.",
            discord.Color.red()
        )
        embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=True)
        embed.add_field(name="💬 Raison", value=reason, inline=False)
        embed.timestamp = datetime.utcnow()
        await ctx.reply(embed=embed)

        log_channel = self.bot.get_channel(self.config_ids["BLACKLIST_LOG_CHANNEL"])
        if log_channel:
            await log_channel.send(embed=embed)

    @commands.hybrid_command(name="delta-unblacklist", description="Retirer un utilisateur de la blacklist")
    async def delta_unblacklist(self, ctx, member: discord.Member, *, reason: str):
        if not self.is_staff(ctx):
            return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

        result = self.collection25.delete_one({"user_id": str(member.id)})
        if result.deleted_count:
            try:
                await member.send(f"✅ Tu as été **retiré de la blacklist** du bot **Project : Delta**.\n**Raison :** `{reason}`")
            except:
                pass

            embed = create_embed(
                "📤 Utilisateur retiré de la blacklist",
                f"{member.mention} a été unblacklist.",
                discord.Color.green()
            )
            embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=True)
            embed.add_field(name="💬 Raison", value=reason, inline=False)
            embed.timestamp = datetime.utcnow()
            await ctx.reply(embed=embed)

            log_channel = self.bot.get_channel(self.config_ids["UNBLACKLIST_LOG_CHANNEL"])
            if log_channel:
                await log_channel.send(embed=embed)
        else:
            await ctx.reply(f"{member.mention} n'était pas blacklist.")

    @commands.hybrid_command(name="delta-list-warn", description="Lister les warns d’un utilisateur")
    async def delta_list_warn(self, ctx, member: discord.Member):
        if not self.is_staff(ctx):
            return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

        warns = list(self.collection24.find({"user_id": str(member.id)}))
        if not warns:
            return await ctx.reply(f"Aucun warn trouvé pour {member.mention}.")

        embed = create_embed(f"⚠️ Warns de {member.display_name}", "", discord.Color.orange())
        for i, warn in enumerate(warns, start=1):
            mod = await self.bot.fetch_user(int(warn['moderator_id']))
            embed.add_field(
                name=f"Warn #{i}",
                value=f"**Par:** {mod.mention}\n**Raison:** `{warn['reason']}`\n**Date:** <t:{int(warn['timestamp'].timestamp())}:R>",
                inline=False
            )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="delta-list-blacklist", description="Lister les utilisateurs blacklist")
    async def delta_list_blacklist(self, ctx):
        if not self.is_staff(ctx):
            return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

        blacklisted = list(self.collection25.find({}))
        if not blacklisted:
            return await ctx.reply("Aucun membre n'est blacklist.")

        embed = create_embed("🚫 Membres blacklist", "", discord.Color.red())
        for i, bl in enumerate(blacklisted, start=1):
            try:
                user = await self.bot.fetch_user(int(bl['user_id']))
                embed.add_field(
                    name=f"Blacklist #{i}",
                    value=f"**Membre :** {user.mention}\n**Raison :** `{bl['reason']}`\n**Date :** <t:{int(bl['timestamp'].timestamp())}:R>",
                    inline=False
                )
            except:
                pass
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))

