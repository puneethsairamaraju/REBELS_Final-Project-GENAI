import discord
import os
import datetime
import random
import re
import csv
from _pipeline import create_payload, model_req

# === Credentials
DISCORD_TOKEN = "MTMzMTM1MzU1NzIwMjUwNTczOQ.GYfyF2.sEZBCFFdLoLe2AOs_3G4ZhKpBHT1va3U2bNBSM"
API_KEY = "sk-7aa9458939d840b78c5b0174f5fa8bd8"
URL_GENERATE = "https://chat.hpc.fau.edu/api/chat/completions"

os.environ["API_KEY"] = API_KEY
os.environ["URL_GENERATE"] = URL_GENERATE

# === Discord Setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# === Memory
user_focus_memory = {}
user_last_challenge = {}
user_session_topics = {}
current_question = {}

# === Motivation
motivations = [
    "🌟 Keep going — you're mastering DSA step by step!",
    "🚀 Progress is built one question at a time. You're doing amazing!",
    "🧠 Every bit of effort counts. Keep it up!",
    "🔥 Great minds are built with persistence. Stay sharp!"
]

async def safe_send(channel, content):
    if len(content) <= 2000:
        await channel.send(content)
    else:
        for i in range(0, len(content), 2000):
            await channel.send(content[i:i+2000])

def log_quiz_attempt(user, question, correct_answer, user_answer, is_correct):
    with open("quiz_log.csv", "a", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.date.today().isoformat(),
            user,
            question.replace("\n", " "),
            correct_answer,
            user_answer,
            "✅" if is_correct else "❌"
        ])

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

        # === Focus
        if user_input.startswith("focus on"):
            topic = user_input.replace("focus on", "").strip()
            if topic:
                user_focus_memory[message.author.id] = topic
                await safe_send(message.channel, f"🧠 Focus updated! I will prioritize **{topic}**.")
            else:
                await safe_send(message.channel, "⚠️ Please specify a topic. Example: `focus on trees`.")
            return

        # === Summarize Session
        if "summarize session" in user_input:
            topics = user_session_topics.get(message.author.id, [])
            if topics:
                summary = "\n".join(f"• {t}" for t in topics)
                await safe_send(message.channel, f"📚 Here's your session summary:\n{summary}")
            else:
                await safe_send(message.channel, "📖 You haven't studied any topic today!")
            return

        # === Greetings and Challenge
        greetings = ["hi", "hello", "hey", "yo", "good morning", "good evening", "start", "let's start", "begin"]
        if any(greet in user_input for greet in greetings) and len(user_input.split()) <= 5:
            await safe_send(message.channel,
                "🤖 Hello! I'm fully operational.\n"
                "Would you like a quiz, explanation, or a coding challenge?\n"
                "Tip: Set focus with `focus on graphs` 📚"
            )
            last_date = user_last_challenge.get(message.author.id)
            if last_date != today:
                user_last_challenge[message.author.id] = today
                focus_topic = user_focus_memory.get(message.author.id)
                if focus_topic:
                    await safe_send(message.channel, f"🌟 Daily Challenge: Solve something about **{focus_topic}**!")
                else:
                    await safe_send(message.channel, "🌟 Daily Challenge: Pick any new DSA topic today!")
            return

        # === Quiz Command
        if user_input.startswith("quiz"):
            await safe_send(message.channel, "📚 Generating your quiz question...")

            prompt = """
Generate a Data Structures and Algorithms multiple-choice question.

Format exactly like this:

Question: <text>
A) <option>
B) <option>
C) <option>
D) <option>
Answer: <letter>
"""

            payload = create_payload(
                target="chat.hpc.fau.edu",
                model="gemini-2.0-flash",
                prompt=prompt,
                temperature=0.4,
                num_ctx=1024,
                num_predict=120
            )

            _, response = model_req(payload)

            if response and "Answer:" in response:
                parts = response.split("Answer:")
                question_text = parts[0].strip()
                correct_answer = parts[1].strip().upper()

                current_question[message.author.id] = {
                    "question": question_text,
                    "answer": correct_answer
                }

                await safe_send(message.channel,
                    f"🧠 **Quiz Time!**\n{question_text}\n\nPlease reply with A, B, C, or D!"
                )
                return
            await safe_send(message.channel, "⚠️ Failed to generate quiz. Try again later.")
            return

        # === Handle Quiz Answer
        if message.author.id in current_question:
            quiz_data = current_question.get(message.author.id)
            match = re.search(r"\b([ABCD])\b", user_input.upper())
            if match:
                user_answer = match.group(1)
                correct = quiz_data["answer"]
                question = quiz_data["question"]

                if user_answer == correct:
                    await safe_send(message.channel, "✅ Correct! 🎉 Great job!")
                    is_correct = True
                else:
                    await safe_send(message.channel, f"❌ Incorrect. The correct answer was **{correct}**.")

                    # 📖 Explain why correct + example
                    explain_prompt = f"""
You are an AI tutor helping a student.

They were asked:
{question}

Student answered {user_answer}, but correct is {correct}.

Explain:
- Why {correct} is correct
- Give a small simple example if possible.

Be concise and clear.
"""
                    payload = create_payload(
                        target="chat.hpc.fau.edu",
                        model="gemini-2.0-flash",
                        prompt=explain_prompt,
                        temperature=0.4,
                        num_ctx=1024,
                        num_predict=250
                    )

                    _, explanation = model_req(payload)
                    await safe_send(message.channel, f"📖 **Explanation:**\n{explanation}")
                    is_correct = False

                log_quiz_attempt(
                    user=str(message.author),
                    question=question,
                    correct_answer=correct,
                    user_answer=user_answer,
                    is_correct=is_correct
                )

                current_question.pop(message.author.id)
                return
            else:
                await safe_send(message.channel, "⚠️ Please reply with A, B, C, or D only.")
            return

        # === Free Chat General (DSA + General Questions)
        await safe_send(message.channel, "🤖 Processing your request...")

        system_prompt = f"""
You are an intelligent and autonomous AI assistant.

Your goals:
- Always answer ANY user question fully (even if not related to DSA).
- If the question is NOT related to DSA, after answering, gently motivate user to return to DSA learning.
- Be friendly, intelligent, supportive, concise, and motivational.

User Focus: {user_focus_memory.get(message.author.id, 'None')}
Topics studied today: {user_session_topics.get(message.author.id, [])}

User Message: {user_input}
"""

        payload = create_payload(
            target="chat.hpc.fau.edu",
            model="gemini-2.0-flash",
            prompt=system_prompt,
            temperature=0.5,
            num_ctx=2048,
            num_predict=300
        )

        _, response = model_req(payload)

        if message.author.id not in user_session_topics:
            user_session_topics[message.author.id] = []
        user_session_topics[message.author.id].append(user_input.title())

        # Answer the user's question
        await safe_send(message.channel, f"🧠 {response}")

        # After any general question, gently suggest to continue DSA learning
        await safe_send(message.channel, "📚 Would you like to continue learning DSA now? I can suggest a quick topic! 🚀")

        if random.random() < 0.3:
            await safe_send(message.channel, random.choice(motivations))

client.run(DISCORD_TOKEN)
