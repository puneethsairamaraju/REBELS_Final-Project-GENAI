import discord
import os
import re
import csv
from datetime import datetime
from _pipeline import create_payload, model_req

# === Credentials (Your hardcoded keys) ===
DISCORD_TOKEN = "MTMzMTM1MzU1NzIwMjUwNTczOQ.GZH_2Y.SJiWvCpVoVM9SezBv1Gr_yqaNNqy1ElSqktEnU"
API_KEY = "sk-7aa9458939d840b78c5b0174f5fa8bd8"
URL_GENERATE = "https://chat.hpc.fau.edu/api/chat/completions"

os.environ["API_KEY"] = API_KEY
os.environ["URL_GENERATE"] = URL_GENERATE

# === Discord Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# === Quiz Tracking ===
current_question = {}

def log_quiz_attempt(user, question, correct_answer, user_answer, is_correct):
    with open("quiz_log.csv", "a", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user,
            question.replace("\n", " "),
            correct_answer,
            user_answer,
            "✅" if is_correct else "❌"
        ])

@client.event
async def on_ready():
    print(f"✅ GenAI Quiz Bot is ready as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        user_input = message.content.replace(f"<@{client.user.id}>", "").strip().lower()

        # === Handle Quiz Command ===
        if user_input.startswith("quiz"):
            await message.channel.send("📚 Generating your quiz question...")

            prompt = """
Generate a Data Structures & Algorithms multiple choice question in this format:

Question: <question>
A) <option>
B) <option>
C) <option>
D) <option>
Answer: <letter>
"""

            payload = create_payload(
                target="chat.hpc.fau.edu",
                model="Llama-3.2-11B-Vision-Instruct",
                prompt=prompt,
                temperature=0.3,
                num_ctx=1024,
                num_predict=100
            )

            _, response = model_req(payload)

            if response:
                parts = response.split("Answer:")
                question_text = parts[0].strip()
                answer = parts[1].strip().upper() if len(parts) > 1 else "?"

                current_question[message.author.id] = {
                    "text": question_text,
                    "answer": answer
                }

                await message.channel.send(
                    f"🧠 **Your Question:**\n{question_text}\n\nReply with A, B, C, or D — or say something like `I think it’s B`."
                )
            else:
                await message.channel.send("⚠️ Could not generate a quiz question.")

        # === Handle Quiz Answers ===
        elif message.author.id in current_question:
            quiz_data = current_question.get(message.author.id)

            match = re.search(r"\b([ABCD])\b", user_input.upper())
            if not match:
                await message.channel.send("🤖 Please respond with A, B, C, or D (or include one in your sentence).")
                return

            user_answer = match.group(1)
            correct = quiz_data["answer"]
            question = quiz_data["text"]

            if user_answer == correct:
                await message.channel.send("✅ Correct! 🎉")
                is_correct = True
            else:
                await message.channel.send(f"❌ Incorrect. The correct answer was **{correct}**.")
                is_correct = False

            log_quiz_attempt(
                user=str(message.author),
                question=question,
                correct_answer=correct,
                user_answer=user_answer,
                is_correct=is_correct
            )

            current_question.pop(message.author.id)

        # === General GenAI Q&A ===
        else:
            await message.channel.send("🧠 Thinking...")

            genai_prompt = f"""
You are a requirement analysis assistant for a DSA Learning Chatbot.
Based on the user's message, extract either a DSA explanation or a functional requirement.

User: {user_input}
"""

            payload = create_payload(
                target="chat.hpc.fau.edu",
                model="Llama-3.2-11B-Vision-Instruct",
                prompt=genai_prompt,
                temperature=0.3,
                num_ctx=2048,
                num_predict=150
            )

            _, response = model_req(payload)
            await message.channel.send(f"✅ Response:\n{response}")

# === Start the bot ===
client.run(DISCORD_TOKEN)
