import discord
import os
from _pipeline import create_payload, model_req

# ✅ Your provided credentials
DISCORD_TOKEN = "MTMzMTM1MzU1NzIwMjUwNTczOQ.GZH_2Y.SJiWvCpVoVM9SezBv1Gr_yqaNNqy1ElSqktEnU"
API_KEY = "sk-7aa9458939d840b78c5b0174f5fa8bd8"
URL_GENERATE = "https://chat.hpc.fau.edu/api/chat/completions"

# Inject credentials into environment for _pipeline.py
os.environ["API_KEY"] = API_KEY
os.environ["URL_GENERATE"] = URL_GENERATE

# Discord setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ✅ Helper function to safely send messages (Discord limit = 2000 chars)
async def safe_send(channel, content):
    if len(content) <= 2000:
        await channel.send(content)
    else:
        for i in range(0, len(content), 2000):
            await channel.send(content[i:i+2000])

@client.event
async def on_ready():
    print(f"✅ AI Assistant is online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        user_input = message.content.replace(f"<@{client.user.id}>", "").strip().lower()

        # ✅ Greet only when appropriate
        greetings = ["hi", "hello", "hey", "yo", "good morning", "good evening"]
        if any(greet in user_input for greet in greetings) and len(user_input.split()) <= 3:
            await safe_send(message.channel,
                "🤖 Hello. I'm fully operational.\n"
                "Would you like to start with a quiz, an explanation, or some code?\n"
                "Just mention me — no commands required."
            )
            return

        await safe_send(message.channel, "🤖 Processing your request...")

        # 🧠 LLM Assistant Prompt
        system_prompt = f"""
You are an intelligent, autonomous assistant for helping users learn Data Structures and Algorithms (DSA).
You act like a highly capable AI. Engage naturally, understand open-ended instructions, offer guidance or suggestions without being prompted.

Respond with clarity and initiative. If the user is unsure, recommend a topic or quiz. 
If they ask about something, explain it, generate code, or quiz them accordingly.

User: {user_input}
Your Response:
"""

        payload = create_payload(
            target="chat.hpc.fau.edu",
            model="Llama-3.2-11B-Vision-Instruct",
            prompt=system_prompt,
            temperature=0.5,
            num_ctx=2048,
            num_predict=200
        )

        _, response = model_req(payload=payload)
        await safe_send(message.channel, f"🧠 {response}")

client.run(DISCORD_TOKEN)
