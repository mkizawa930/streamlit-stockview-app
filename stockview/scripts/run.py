import contextlib
import io
import os
import tempfile
from logging import getLogger

import discord
import discord.ext.commands as commands
import mdutils
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from table2ascii import PresetStyle
from table2ascii import table2ascii as t2a

from stockview.app import analysis
from stockview.app.data import fetch

logger = getLogger("discord")

load_dotenv()

TOKEN = os.environ["DISCORD_TOKEN"]
if not TOKEN:
    raise Exception("Discordトークンが見つかりません")

CHANNEL_ID = 1090980455714672751

intents = discord.Intents.all()
# intents.message_content = True
client = commands.Bot(command_prefix="", intents=intents)


@contextlib.contextmanager
def generate_image_file(fig: plt.Figure):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    buf.seek(0)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as t:
        with open(t.name, "+ab") as file:
            file.write(buf.getvalue())
            file.seek(0)
            yield file


@client.event
async def on_ready():
    logger.info("bot is ready")
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        pass

    df = fetch()
    await channel.send(df.iloc[-1, :].to_markdown())

    # mdFile = mdutils.MdUtils(file_name="temp")
    ohlcv = df.iloc[-1, :]

    output = t2a(
        # header=["Column", "Value"],
        body=[
            ["open", "{}()".format(round(ohlcv.open, 2))],
            ["high", round(ohlcv.high, 2)],
            ["low", round(ohlcv.low, 2)],
            ["close", round(ohlcv.close, 2)],
        ],
        style=PresetStyle.thin_compact,
    )

    await channel.send(f"```{output}```")

    # df = analysis.analyze(df)
    # fig, _ = analysis.create_canldestick_chart(df)
    # with generate_image_file(fig) as file:
    #     await channel.send(file=discord.File(file))

    # fig, _ = analysis.create_analyzed_chart(df)
    # with generate_image_file(fig) as file:
    #     await channel.send(file=discord.File(file))

    logger.info("exit")
    await client.close()


# @client.event
# async def on_message(message):
#     print(message)
#     channel = client.get_channel(1090980455714672751)
#     await channel.send(f"{message}")


# async def greet():
#     channel = client.get_channel(1090980455714672751)
#     await channel.send("テスト")

if __name__ == "__main__":
    client.run(TOKEN)
