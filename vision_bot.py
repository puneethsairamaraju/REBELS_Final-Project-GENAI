import discord
import os
import datetime
import random
from _pipeline import create_payload, model_req

# ✅ Your provided credentials
DISCORD_TOKEN = "MTMzMTM1MzU1NzIwMjUwNTczOQ.GZH_2Y.SJiWvCpVoVM9SezBv1Gr_yqaNNqy1ElSqktEnU"
API_KEY = "sk-7aa9458939d840b78c5b0174f5fa8bd8"
URL_GENERATE = "https://chat.hpc.fau.edu/api/chat/completions"

# Inject credentials for _pipeline.py
os.environ["API_KEY"] = API_KEY
os.environ["URL_GENERATE"] = URL_GENERATE

# Discord setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 🧠 Memory Structures
user_focus_memory = {}
user_last_challenge = {}
user_session_topics = {}
user_confidence_scores = {}

# Motivational Quotes
motivations = [
    "🌟 Keep going — you're mastering DSA step by step!",
    "🚀 Progress is built one question at a time. You're doing amazing!",
    "🧠 Every bit of effort counts. Keep it up!",
    "🔥 Great minds are built with persistence. Stay sharp!"
]

# ✅ Safe send to avoid Discord limit
async def safe_send(channel, content):
    if len(content) <= 2000:
        await channel.send(content)
    else:
        for i in range(0, len(content), 2000):
            await channel.send(content[i:i+2000])

@client.event
async def on_ready():
    print(f"✅ AI Final Assistant is online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        user_input = message.content.replace(f"<@{client.user.id}>", "").strip().lower()

        today = datetime.date.today().isoformat()

        # ✅ Handle setting focus topic
        if user_input.startswith("focus on"):
            topic = user_input.replace("focus on", "").strip()
            if topic:
                user_focus_memory[message.author.id] = topic
                await safe_send(message.channel, f"🧠 Focus updated! I will prioritize **{topic}** in future discussions and challenges.")
            else:
                await safe_send(message.channel, "⚠️ Please specify a topic. Example: `focus on trees`.")
            return

        # ✅ Handle session summary request
        if "summarize session" in user_input:
            topics = user_session_topics.get(message.author.id, [])
            if topics:
                summary = "\n".join(f"• {t}" for t in topics)
                await safe_send(message.channel, f"📚 Here's what you covered today:\n{summary}")
            else:
                await safe_send(message.channel, "📖 You haven't studied anything today yet!")
            return

        # ✅ Greeting or Daily Challenge
        greetings = ["hi", "hello", "hey", "yo", "good morning", "good evening", "start", "let's start", "begin"]
        if any(greet in user_input for greet in greetings) and len(user_input.split()) <= 5:
            await safe_send(message.channel,
                "🤖 Hello! I'm fully operational.\n"
                "Would you like a quiz, explanation, or a coding challenge?\n"
                "You can also set your focus with `focus on graphs` 📚"
            )

            # Daily Challenge Trigger
            last_date = user_last_challenge.get(message.author.id)
            if last_date != today:
                user_last_challenge[message.author.id] = today
                focus_topic = user_focus_memory.get(message.author.id)
                if focus_topic:
                    challenge_text = f"🌟 Today's challenge: Solve or explore something related to **{focus_topic}**!"
                else:
                    challenge_text = "🌟 Today's challenge: Explore a new DSA topic! Shall I suggest one?"
                await safe_send(message.channel, challenge_text)

            return

        await safe_send(message.channel, "🤖 Processing your request...")

        # 🧠 Personalized LLM Prompt
        system_prompt = f"""
You are an intelligent, autonomous assistant helping users learn Data Structures and Algorithms (DSA).
Adapt to user interests, focus topics, and suggest personalized challenges when possible.

User's current focus topic: {user_focus_memory.get(message.author.id, 'None')}

Session topics studied today: {user_session_topics.get(message.author.id, [])}

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

        # ✅ Save topic to session memory
        if message.author.id not in user_session_topics:
            user_session_topics[message.author.id] = []
        user_session_topics[message.author.id].append(user_input.title())

        await safe_send(message.channel, f"🧠 {response}")

        # ✅ Random Motivational Boost
        if random.random() < 0.3:  # 30% chance after every interaction
            await safe_send(message.channel, random.choice(motivations))

        # ✅ Ask for Confidence Score
        await safe_send(message.channel, "🎯 On a scale of 1-5, how confident do you feel about this topic? (Reply `@Rebels 4`, for example)")

    # ✅ Handle Confidence Score Responses
    elif message.content.strip().isdigit() and message.reference:
        referenced = await message.channel.fetch_message(message.reference.message_id)
        if client.user in referenced.mentions:
            score = int(message.content.strip())
            if 1 <= score <= 5:
                user_confidence_scores.setdefault(message.author.id, []).append(score)
                await safe_send(message.channel, "✅ Confidence score saved! Keep pushing forward!")

client.run(DISCORD_TOKEN)
