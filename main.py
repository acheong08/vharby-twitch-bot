from twitchio.ext import commands
from twitchio.message import Message
from revChatGPT.V3 import Chatbot
from EdgeGPT import Chatbot as Edgebot
import os
import re
import time


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
        self.edgebot = Edgebot(cookiePath="./cookies.json")
        self.limit_timer = 0

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
        # If the timer is less than 20 seconds, return
        if time.time() - self.limit_timer < 60:
            return
        # Split the message into command and arguments
        command, *args = msg_details.message.split(" ")
        if command == "&chatgpt":
            print("ChatGPT running")
            prompt = " ".join(args)
            response = self.chatbot.ask(prompt, max_tokens=100).replace("\n", "")
            # Loop and send response in chunks of 200 characters
            for i in range(0, len(response), 150):
                await context.send(response[i : i + 150])
                print("Sent: ", response[i : i + 150])
                time.sleep(1.5)
        elif command == "&ping":
            await context.send(f"Pong! {msg_details.author}")
        elif command == "&edgegpt":
            print("EdgeGPT running")
            prompt = " ".join(args)
            response = await self.edgebot.ask(prompt=prompt)
            response = response["item"]["messages"][1]["text"].replace("\n", "")
            print("Response: ", response)
            # Loop and send response in chunks of 200 characters
            for i in range(0, len(response), 150):
                await context.send(response[i : i + 150])
                time.sleep(1.5)

        # Set a timer to prevent spamming
        self.limit_timer = time.time()


bot = Bot()
bot.run()
