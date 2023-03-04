from twitchio.ext import commands
from twitchio.message import Message
from revChatGPT.V3 import Chatbot
import os
import re


class CustomMsgDetails:
    def __init__(self):
        self.message: str = None
        self.author: str = None
        self.isYouTube: bool = False


class Bot(commands.Bot):
    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(
            token=os.environ.get("access_token"),
            prefix="<BOT>",
            initial_channels=["virtualharby"],
        )
        # self.bot = Chatbot(os.environ.get("email"), os.environ.get("password"))
        self.chatbot = Chatbot(
            api_key=os.environ.get("api_key"),
        )

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")

    async def event_message(self, message: Message) -> None:
        if message.echo:
            return
        msg_details = CustomMsgDetails()
        context = await self.get_context(message)
        # Re search for [YouTube: *] in message.content and if found
        yt_match = re.search(r"\[YouTube: (.*)\]", message.content)
        msg_details.message = message.content
        if yt_match:
            msg_details.author = yt_match.group(1)
            msg_details.isYouTube = True
            # replace [YouTube: *] with nothing
            msg_details.message = message.content.replace(
                f"[YouTube: {msg_details.author}] ", ""
            ).rstrip()
        else:
            msg_details.author = message.author.name

        if msg_details.message.startswith("&"):
            await self.handle_commands(context, msg_details)
        if msg_details.author == "nightbot":
            await context.send(f"{msg_details.author}: {msg_details.message}")
        elif msg_details.isYouTube and msg_details.message.startswith("!"):
            await context.send(msg_details.message)

    async def handle_commands(
        self, context: commands.Context, msg_details: CustomMsgDetails
    ):
        # Split the message into command and arguments
        command, *args = msg_details.message.split(" ")
        if command == "&chatgpt":
            prompt = " ".join(args)
            response = self.chatbot.ask(prompt)
            await context.send(response)


bot = Bot()
bot.run()
