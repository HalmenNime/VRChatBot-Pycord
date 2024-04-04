import discord
from discord.ext import commands
from termcolor import colored
from datetime import datetime
import requests
import os
import shutil
import git

if not os.path.exists(".env"):
    if os.path.exists("example.env"):
        shutil.copy("example.env", ".env")
        print(colored("File .env was not find, now created, please edit and start bot again!", "yellow"))
    else:
        print(colored("File .env was not find, create please and check example env in repository for copy and edit!", "yellow"))
    exit()


if os.getenv("REPOSITORY_UPDATE_NOTIFICATION", "True") == "True":
    try:
        repo = git.Repo()
        origin = repo.remote()
        origin.fetch()

        local_version = repo.head.commit.hexsha
        remote_version = origin.refs[0].commit.hexsha

        if local_version != remote_version:
            commit_difference = len(list(origin.refs[0].commit.iter_items())) - len(list(repo.iter_commits()))
            print(f"There's an update in repository, local repository is behind by {commit_difference} commits")

    except git.exc.InvalidGitRepositoryError:
        print("This is not a valid Git repository")
    except git.exc.GitCommandError as e:
        print(f"Error retrieving updates from remote repository: {e}")


class WorldView(discord.ui.View):
    def __init__(self, world_name, world_bio, world_image, world_favorites, world_visits, world_authorName, world_platform):
        super().__init__(timeout=10)
    
        self.world_name = world_name
        self.world_bio = world_bio
        self.world_image = world_image
        self.world_favorites = world_favorites
        self.world_visits = world_visits
        self.world_authorName = world_authorName
        self.world_platform = world_platform
    
    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit(view=self)
    
    @discord.ui.button(label="Info World", style=discord.ButtonStyle.primary, emoji="🌆")
    async def button_callback(self, button, interaction):
        
        embed = discord.Embed(title=f"{self.world_name}", description=f"Description: {self.world_bio}", color=discord.Color.blue())
        embed.add_field(name="Author", value=self.world_authorName, inline=False)
        embed.add_field(name="Favorites", value=self.world_favorites, inline=False)
        embed.add_field(name="Visits", value=self.world_visits, inline=False)
        embed.set_thumbnail(url=self.world_image)
        
        await interaction.response.send_message(embed=embed)

language_emojis = {
    "language_rus": "🇷🇺",
    "language_eng": "🇬🇧",
    "language_ukr": "🇺🇦",
    "language_deu": "🇩🇪",
    "language_fra": "🇫🇷",
    "language_spa": "🇪🇸",
    "language_por": "🇵🇹",
    "language_jpn": "🇯🇵",
    "language_ase": "🇦🇪",
    "language_kor": "🇰🇷",
    "language_zho": "🇨🇳",
    "language_ita": "🇮🇹",
    "language_pol": "🇵🇱",
    "language_tha": "🇹🇭",
    "language_nld": "🇳🇱",
    "language_ara": "🇦🇷",
    "language_dan": "🇩🇰",
    "language_nor": "🇳🇴",
    "language_tur": "🇹🇷",
    "language_swe": "🇸🇪",
    "language_vie": "🇻🇮",
    "language_ind": "🇮🇳",
    "language_tgl": "🇹🇬",
    "language_ces": "🇨🇿",
    "language_fin": "🇫🇮",
    "language_bfi": "🇧🇫",
    "language_ron": "🇷🇴",
    "language_hun": "🇭🇺",
}

platform_emojis = {
    "windows": "<:windows:1224011075599601674>",
    "android": "<:android:1224012767040634920>",
    "quest": "<:meta:1224015480696869104>"
}

intents = discord.Intents().all()
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} started")

async def get_info_user(id):
    url = f"https://api.vrchat.cloud/api/1/users/{id}"
    headers = {
        "User-Agent": "MyApp/1.0 (contact@example.com)",
        "Cookie": f"auth={os.getenv('COOKIE_AUTH', 'YOUR_COOKIE_AUTH')}"
    }
    response = requests.get(url, headers=headers)
    if os.getenv("DEBUG_API_RESPONSE_CONSOLE", "False") == "True":
        print(response.json())

    return response

async def get_info_worldId(id):
    url = f"https://api.vrchat.cloud/api/1/worlds/{id}"
    headers = {
        "User-Agent": "MyApp/1.0 (contact@example.com)",
        "Cookie": f"auth={os.getenv('COOKIE_AUTH', 'YOUR_COOKIE_AUTH')}"
    }
    response = requests.get(url, headers=headers)
    if os.getenv("DEBUG_API_RESPONSE_CONSOLE", "False") == "True":
        print(response.json())

    return response

@bot.slash_command(description = "Check profile VRChat user")
async def profile(ctx, id = discord.Option(str, description="Check information about user VRChat via ID")):
    
    response = await get_info_user(id)

    if response.status_code == 200:
        data = response.json()
        currentAvatarThumbnail = data["currentAvatarThumbnailImageUrl"]
        username = data["displayName"]
        bio = data["bio"]
        last_platform = data["last_platform"]
        tags = data["tags"]
        state = data["state"]
        view = None
        langs = ','.join(language_emojis[tag] for tag in tags if tag in language_emojis) or "Not specified"
        
        if len(bio) < 1:
            bio = 'Not specified'
        
        if state == "online":
            state = "Online 🟢"
            worldID = data["worldId"]
            if worldID != "offline":
                world = await get_info_worldId(worldID)
                data2 = world.json()
                if world.status_code == 404:
                    state += f" (In a private world)"
                else:
                    world_name = data2["name"]
                    state += f" (Playing in {world_name})"
                    world_bio = data2["description"]
                    world_image = data2["imageUrl"]
                    world_favorites = data2["favorites"]
                    world_visits = data2["visits"]
                    world_authorName = data2["authorName"]
                    world_platform = data2["unityPackages"]["platform"]
                    view = WorldView(world_name=world_name, world_bio=world_bio, world_image=world_image, world_favorites=world_favorites, world_visits=world_visits, world_authorName=world_authorName, world_platform=world_platform)

                
        elif state == "offline":
            state = "Offline 🔴"
        elif state == "active":
            state = "Active 🔵"
        else:
            state = f"{state} ❓"

        if last_platform == "standalonewindows":
            last_platform = f"Windows {platform_emojis['windows']}"
        elif last_platform == "android":
            last_platform = f"Android {platform_emojis['android']} or Quest {platform_emojis['quest']}"
        else:
            last_platform = f"{last_platform} ❓"
        
        embed = discord.Embed(title=f"Information about {username}", description=f"Bio: {bio}", color=discord.Color.blue())
        embed.add_field(name="Platform:", value=last_platform, inline=False)
        embed.add_field(name="State:", value=state, inline=False)
        embed.add_field(name="Languages:", value=langs, inline=False)
        embed.set_author(name="VRChat info", url="https://www.google.com/url?sa=i&url=https%3A%2F%2Fask.vrchat.com%2Ftag%2Fbug&psig=AOvVaw373wKWlf86aLr1OofimNsY&ust=1711971065371000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCKiK7qyznoUDFQAAAAAdAAAAABAJ")
        embed.set_thumbnail(url=currentAvatarThumbnail)
        await ctx.respond(embed=embed, view=view)
    
    elif response.status_code == 404:
        embed = discord.Embed(title="Error", description=f"User not found", color=discord.Color.red())
        await ctx.respond(embed=embed)
    
    elif response.status_code == 401:
        embed = discord.Embed(title="Error", description=f"Missing Credentials, something wrong with auth cookie", color=discord.Color.red())
        await ctx.respond(embed=embed)
    
    else:
        embed = discord.Embed(title="Error", description=f"Unexpected error code ``({response.status_code})``, more detail will show in logs", color=discord.Color.red())
        await ctx.respond(embed=embed)
        print(response.json())

try:
    bot.run(os.getenv('TOKEN_BOT', 'YOUR_TOKEN_BOT'))
except discord.errors.LoginFailure as e:
    print(colored(f"Fail login in bot, wrong token?: {e}", "yellow"))
except Exception as e:
    print(colored(f"Something problem with login in bot: {e}", "yellow"))