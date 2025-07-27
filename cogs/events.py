import discord
from discord.ext import commands
from datetime import datetime
import traceback

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ Le bot {self.bot.user} est maintenant connecté ! (ID: {self.bot.user.id})")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channel_id = 1361304582424232037  # ID du salon cible
        channel = self.bot.get_channel(channel_id)

        if channel is None:
            channel = await self.bot.fetch_channel(channel_id)

        total_guilds = len(self.bot.guilds)
        total_users = sum(guild.member_count for g in self.bot.guilds)

        embed = discord.Embed(
            title="✨ Nouveau serveur rejoint !",
            description="Le bot a été ajouté sur un nouveau serveur.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="📛 Nom", value=guild.name, inline=True)
        embed.add_field(name="🆔 ID", value=guild.id, inline=True)
        embed.add_field(name="👥 Membres", value=str(guild.member_count), inline=True)
        embed.add_field(name="👑 Propriétaire", value=str(guild.owner), inline=True)
        embed.add_field(name="🌍 Région", value=guild.preferred_locale, inline=True)
        embed.add_field(name="🔢 Total serveurs", value=str(total_guilds), inline=True)
        embed.add_field(name="🌐 Utilisateurs totaux (estimation)", value=str(total_users), inline=True)
        embed.set_footer(text="Ajouté le")

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        channel_id = 1361306217460531225  # ID du salon cible
        channel = self.bot.get_channel(channel_id)

        if channel is None:
            channel = await self.bot.fetch_channel(channel_id)

        total_guilds = len(self.bot.guilds)
        total_users = sum(g.member_count for g in self.bot.guilds if g.member_count)

        embed = discord.Embed(
            title="💔 Serveur quitté",
            description="Le bot a été retiré d’un serveur.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="📛 Nom", value=guild.name, inline=True)
        embed.add_field(name="🆔 ID", value=guild.id, inline=True)
        embed.add_field(name="👥 Membres lors du départ", value=str(guild.member_count), inline=True)
        embed.add_field(name="👑 Propriétaire", value=str(guild.owner), inline=True)
        embed.add_field(name="🌍 Région", value=guild.preferred_locale, inline=True)
        embed.add_field(name="🔢 Total serveurs restants", value=str(total_guilds), inline=True)
        embed.add_field(name="🌐 Utilisateurs totaux (estimation)", value=str(total_users), inline=True)
        embed.set_footer(text="Retiré le")

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.bot or message.guild is None:
                return

            user_id = str(message.author.id)

            # 🚫 1. Blacklist : ignore tous les messages sauf si mot sensible
            blacklisted = self.bot.db_collections["delta_bl"].find_one({"user_id": user_id})
            if blacklisted:
                for word in sensitive_categories:
                    if re.search(rf"\b{re.escape(word)}\b", message.content, re.IGNORECASE):
                        print(f"🚨 Mot sensible détecté (blacklisté) dans le message de {message.author}: {word}")
                        asyncio.create_task(send_alert_to_admin(message, word))
                        break
                return

            # 💬 2. Vérifie les mots sensibles
            for word in word_to_category:
                if re.search(rf"\b{re.escape(word)}\b", message.content, re.IGNORECASE):
                    category = word_to_category[word.lower()]
                    guild_settings = self.bot.db_collections["sensible"].find_one({"guild_id": str(message.guild.id)})
                    if guild_settings and not guild_settings.get(category, True):
                        print(f"❌ Catégorie {category} désactivée, pas d'alerte.")
                        break
                    print(f"🚨 Mot sensible détecté dans le message de {message.author}: {word}")
                    asyncio.create_task(send_alert_to_admin(message, word))
                    break

            # 📣 3. Répond si le bot est mentionné
            if self.bot.user.mentioned_in(message) and message.content.strip().startswith(f"<@{self.bot.user.id}>"):
                avatar_url = self.bot.user.avatar.url if self.bot.user.avatar else None

                embed = discord.Embed(
                    title="👋 Besoin d’aide ?",
                    description=(
                        f"Salut {message.author.mention} ! Moi, c’est **{self.bot.user.name}**, ton assistant sur ce serveur. 🤖\n\n"
                        "🔹 **Pour voir toutes mes commandes :** Appuie sur le bouton ci-dessous ou tape `+help`\n"
                        "🔹 **Une question ? Un souci ?** Contacte le staff !\n\n"
                        "✨ **Profite bien du serveur et amuse-toi !**"
                    ),
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=avatar_url)
                embed.set_footer(text="Réponse automatique • Disponible 24/7", icon_url=avatar_url)

                view = View()
                button = Button(label="📜 Voir les commandes", style=discord.ButtonStyle.primary)

                async def button_callback(interaction: discord.Interaction):
                    ctx = await self.bot.get_context(interaction.message)
                    await ctx.invoke(self.bot.get_command("help"))
                    await interaction.response.send_message("Voici la liste des commandes !", ephemeral=True)

                button.callback = button_callback
                view.add_item(button)

                await message.channel.send(embed=embed, view=view)
                return

            # ⚙️ 4. Configuration sécurité
            guild_data = self.collection.find_one({"guild_id": str(message.guild.id)})
            if not guild_data:
                await self.bot.process_commands(message)
                return

            # 🔗 5. Anti-lien
            if guild_data.get("anti_link", False):
                if "discord.gg" in message.content and not message.author.guild_permissions.administrator:
                    whitelist_data = await self.collection19.find_one({"guild_id": str(message.guild.id)})
                    wl_ids = whitelist_data.get("users", []) if whitelist_data else []

                    if str(message.author.id) in wl_ids:
                        print(f"[Anti-link] Message de {message.author} ignoré (whitelist).")
                        return

                    await message.delete()
                    await message.author.send("⚠️ Les liens Discord sont interdits sur ce serveur.")
                    return

            # 💣 6. Anti-spam
            if guild_data.get("anti_spam_limit"):
                whitelist_data = await self.collection19.find_one({"guild_id": str(message.guild.id)})
                wl_ids = whitelist_data.get("users", []) if whitelist_data else []

                if str(message.author.id) in wl_ids:
                    print(f"[Anti-spam] Message de {message.author} ignoré (whitelist).")
                    return

                now = time.time()
                uid = message.author.id
                user_messages.setdefault(uid, []).append(now)

                recent = [t for t in user_messages[uid] if t > now - 5]
                user_messages[uid] = recent

                if len(recent) > 10:
                    await message.guild.ban(message.author, reason="Spam excessif")
                    return

                per_minute = [t for t in recent if t > now - 60]
                if len(per_minute) > guild_data["anti_spam_limit"]:
                    await message.delete()
                    await message.author.send("⚠️ Vous envoyez trop de messages trop rapidement. Réduisez votre spam.")
                    return

            # 📣 7. Anti-everyone
            if guild_data.get("anti_everyone", False):
                if "@everyone" in message.content or "@here" in message.content:
                    whitelist_data = await self.collection19.find_one({"guild_id": str(message.guild.id)})
                    wl_ids = whitelist_data.get("users", []) if whitelist_data else []

                    if str(message.author.id) in wl_ids:
                        print(f"[Anti-everyone] Message de {message.author} ignoré (whitelist).")
                        return

                    await message.delete()
                    await message.author.send("⚠️ L'utilisation de `@everyone` ou `@here` est interdite sur ce serveur.")
                    return

            # ✅ 8. Traitement normal
            await self.bot.process_commands(message)

        except Exception:
            print("❌ Erreur dans on_message :")
            traceback.print_exc()

async def setup(bot):
    await bot.add_cog(Events(bot))

