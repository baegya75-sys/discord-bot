import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import os

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

MANAGER_ROLE_NAME = "₊˚ ꒰ 🍡 ꒱ᆞ관리진"

class StatusChanger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="상태변경", description="봇의 상태(온라인/자리비움/방해금지)를 변경합니다.")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="온라인", value="online"),
            app_commands.Choice(name="자리비움", value="idle"),
            app_commands.Choice(name="방해금지", value="dnd"),
        ]
    )
    async def 상태변경(self, interaction: discord.Interaction, mode: app_commands.Choice[str]):
        status_mapping = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
        }

        status = status_mapping.get(mode.value)

        if status:
            await self.bot.change_presence(
                status=status,
                activity=discord.Game(name="서버 지켜보는 중")
            )

            emoji = {
                "online": "🟢",
                "idle": "🟡",
                "dnd": "🔴"
            }.get(mode.value, "ℹ️")

            await interaction.response.send_message(
                f"{emoji} 상태를 **{mode.name}**(으)로 변경했어요!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "상태 변경에 실패했어요.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(StatusChanger(bot))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="서버 지켜보는 중"))
    try:
        synced = await bot.tree.sync()
        print(f"✅ 로그인 완료: {bot.user} / 슬래시 명령 {len(synced)}개 동기화됨")
    except Exception as e:
        print(f"❌ 슬래시 명령 동기화 실패: {e}")


@bot.tree.command(name="안내시작", description="새 유저에게 역할과 닉네임을 자동으로 설정합니다.")
@app_commands.describe(
    user="안내할 유저",
    성별="유저의 성별",
    나이="유저의 나이",
    닉네임="바꿀 닉네임"
)
@app_commands.checks.has_role(MANAGER_ROLE_NAME)
async def 안내시작(
    interaction: discord.Interaction,
    user: discord.Member,
    성별: str,
    나이: str,
    닉네임: str
):
    try:
        await interaction.response.defer()

        role_names = [
            "⟡ -------- ˚₊· ☁️ ·₊˚ -------- ⟡",
            "⟡ -------- ˚₊· 🪔 ·₊˚ -------- ⟡",
            "⟡ -------- ˚₊· 🎀 ·₊˚ -------- ⟡",
            "⟡ -------- ˚₊· 🎮 ·₊˚ -------- ⟡",
            "⟡ -------- ˚₊· 🌿 ·₊˚ -------- ⟡",
            "₊˚ ꒰ 🍥 ꒱ᆞ멤버"
        ]

        age_roles = {
            "미자": "₊˚ ꒰ 🐣 ꒱ᆞ미자",
            "성인": "₊˚ ꒰ 🦢 ꒱ᆞ성인"
        }

        if 나이 in age_roles:
            role_names.append(age_roles[나이])

        if 성별 == "남":
            role_names.append("₊˚ ꒰ 🩵 ꒱ᆞ남자")
        elif 성별 == "여":
            role_names.append("₊˚ ꒰ 🩷 ꒱ᆞ여자")

        for name in role_names:
            role = discord.utils.get(interaction.guild.roles, name=name)
            if role:
                await user.add_roles(role)
            else:
                await interaction.followup.send(f"역할 {name} 을 찾을 수 없습니다.")
                return

        # ✅ 닉네임 변경: 뉴페이스 (닉네임)
        new_nick = f"✧ ₊˚ 🫙 ︰{닉네임} ♡"
        await user.edit(nick=new_nick)

        await interaction.followup.send(
            f"{user.mention}에게 역할과 닉네임이 성공적으로 업데이트되었습니다."
        )

        WELCOME_CHANNEL_ID = 1473520202720481280
        welcome_channel = interaction.guild.get_channel(WELCOME_CHANNEL_ID)

        if welcome_channel:
            NEW_FACE_ROLE_ID = 1434890728999223387
            mention_line = f"{user.mention} <@&{NEW_FACE_ROLE_ID}>"

            embed = discord.Embed(
                title="환영합니다",
                description="좋은 서버 활동 해주세요",
                color=discord.Color.purple()
            )

            await welcome_channel.send(content=mention_line, embed=embed)

    except Exception as e:
        print(f"❌ [안내시작 오류] {e}")
        try:
            await interaction.followup.send("오류가 발생했어요.")
        except:
            pass


@안내시작.error
async def 안내시작_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message(
            "이 명령어는 관리자만 사용할 수 있습니다.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"오류 발생: {error}",
            ephemeral=True
        )


@bot.tree.command(name="종료", description="봇 종료 하는 명령어")
@app_commands.checks.has_permissions(administrator=True)
async def shutdown(interaction: discord.Interaction):
    await interaction.response.send_message("봇 종료 중", ephemeral=True)
    await bot.close()

@shutdown.error
async def shutdown_error(interaction: discord.Interaction, error):
    await interaction.response.send_message("관리자만 사용 가능", ephemeral=True)

bot.run(os.getenv("TOKEN"))