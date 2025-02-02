from typing import List, Dict
import sqlite3
from datetime import datetime
import os
from openai import OpenAI
import click
from dotenv import load_dotenv

load_dotenv()


class ConversationStore:
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Existing conversations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    sender TEXT,
                    receiver TEXT,
                    message TEXT
                )
            """
            )

            # New global summaries table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS global_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    summary TEXT,
                    conversation_start_id INTEGER,
                    conversation_end_id INTEGER
                )
            """
            )

            conn.commit()
            conn.close()
        except Exception as e:
            click.secho(f"Database setup failed: {e}", fg="red")
            raise

    def store_message(self, sender: str, receiver: str, message: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (timestamp, sender, receiver, message) VALUES (?, ?, ?, ?)",
            (datetime.now(), sender, receiver, message),
        )
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return message_id

    def store_global_summary(self, summary: str, start_id: int, end_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO global_summaries (timestamp, summary, conversation_start_id, conversation_end_id) VALUES (?, ?, ?, ?)",
            (datetime.now(), summary, start_id, end_id),
        )
        conn.commit()
        conn.close()

    def get_recent_messages(self, limit: int = 5) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, timestamp, sender, receiver, message 
            FROM conversations 
            ORDER BY timestamp DESC 
            LIMIT ?
        """,
            (limit,),
        )

        messages = [
            {
                "id": row[0],
                "timestamp": row[1],
                "sender": row[2],
                "receiver": row[3],
                "message": row[4],
            }
            for row in cursor.fetchall()
        ]
        conn.close()
        return messages[::-1]  # Return in chronological order

    def get_global_summaries(self, limit: int = 3) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT timestamp, summary 
            FROM global_summaries 
            ORDER BY timestamp DESC 
            LIMIT ?
        """,
            (limit,),
        )

        summaries = [{"timestamp": row[0], "summary": row[1]} for row in cursor.fetchall()]
        conn.close()
        return summaries


def generate_global_summary(client: OpenAI, recent_messages: List[Dict], previous_summaries: List[Dict]) -> str:
    # Combine previous summaries and recent messages into context
    previous_context = "\n".join([f"Previous Summary ({s['timestamp']}): {s['summary']}" for s in previous_summaries])

    recent_context = "\n".join([f"{msg['sender']} → {msg['receiver']}: {msg['message']}" for msg in recent_messages])

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                    Create a concise summary of both the previous context and the recent conversation.
                    Focus on key points, decisions, and evolving themes.
                    This summary will serve as long-term memory for future conversations.
                    Keep it to 2-3 sentences.""",
                },
                {
                    "role": "user",
                    "content": f"""
                    Previous Summaries:
                    {previous_context}
                    
                    Recent Conversation:
                    {recent_context}
                    
                    Provide a global summary:""",
                },
            ],
            temperature=0.7,
            max_tokens=360,
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        click.secho(f"Error generating global summary: {e}", fg="red")
        return "Error generating summary"


class Agent:
    def __init__(self, name: str, profile: Dict):
        self.name = name
        self.profile = profile
        self.client = OpenAI()
        click.secho(f"Created agent: {name} - {profile['occupation']}", fg="blue")

    def generate_next_message(
        self,
        conversation_history: List[Dict],
        global_summaries: List[Dict],
        available_receivers: List[str],
    ) -> tuple:
        """Generates next message using both recent and long-term memory."""
        # Combine global summaries and recent history
        context = ""
        if global_summaries:
            context += "Long-term Context:\n" + "\n".join([f"Previous Summary: {s['summary']}" for s in global_summaries]) + "\n\n"

        context += "Recent Conversation:\n" + "\n".join([f"{msg['sender']} → {msg['receiver']}: {msg['message']}" for msg in conversation_history])

        try:
            # First, decide who to talk to
            receiver_prompt = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"""
                        You are {self.name}, a {self.profile['occupation']}. 
                        Based on the complete context, choose ONE person to talk to next from: {', '.join(available_receivers)}.
                        Only respond with the name, nothing else.""",
                    },
                    {
                        "role": "user",
                        "content": f"{context}\n\nWho will you talk to next?",
                    },
                ],
                temperature=0.7,
                max_tokens=20,
            )

            next_receiver = receiver_prompt.choices[0].message.content.strip()
            if next_receiver not in available_receivers:
                next_receiver = available_receivers[0]  # fallback

            # Then, generate the message
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"""
                        You are {self.name}, a {self.profile['occupation']}.
                        Generate a natural response continuing the conversation with {next_receiver}.
                        Consider both the long-term context and recent conversation.
                        Keep it concise (2-3 sentences) and relevant.""",
                    },
                    {
                        "role": "user",
                        "content": f"{context}\n\nGenerate your next message to {next_receiver}:",
                    },
                ],
                temperature=0.7,
                max_tokens=150,
            )

            message = response.choices[0].message.content.strip()
            return next_receiver, message

        except Exception as e:
            click.secho(f"Error generating response: {e}", fg="red")
            return available_receivers[0], f"Error generating response: {str(e)}"


def main():
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is not set!")

        store = ConversationStore()
        client = OpenAI()

        # Initialize agents
        agents = {
            "Alice": Agent("Alice", {"occupation": "Software Engineer"}),
            "Bob": Agent("Bob", {"occupation": "Data Scientist"}),
            "Charlie": Agent("Charlie", {"occupation": "Product Manager"}),
        }

        # Get both recent messages and global summaries
        recent_messages = store.get_recent_messages()
        global_summaries = store.get_global_summaries()

        if global_summaries:
            click.secho("\nLong-term Context:", fg="yellow")
            for summary in global_summaries:
                click.secho(f"Previous Summary: {summary['summary']}", fg=(127, 255, 212))

        if recent_messages:
            click.secho("\nRecent conversation history:", fg="yellow")
            for msg in recent_messages:
                click.secho(
                    f"{msg['sender']} → {msg['receiver']}: {msg['message']}",
                    fg=(127, 255, 212),
                )

        # Track conversation bounds for summary
        first_message_id = None
        last_message_id = None

        # Run conversation rounds
        for round_num in range(3):
            click.secho(f"\nRound {round_num + 1}:", fg="yellow")

            for agent_name, agent in agents.items():
                available_receivers = [name for name in agents.keys() if name != agent_name]
                history = store.get_recent_messages()
                global_summaries = store.get_global_summaries()

                receiver, message = agent.generate_next_message(history, global_summaries, available_receivers)

                message_id = store.store_message(agent_name, receiver, message)

                if first_message_id is None:
                    first_message_id = message_id
                last_message_id = message_id

                click.secho(f"{agent_name} → {receiver}: {message}", fg=(255, 105, 180))

        # Generate and store global summary
        click.secho("\nGenerating global summary...", fg="yellow")
        final_messages = store.get_recent_messages(limit=9)  # Get messages from this session
        previous_summaries = store.get_global_summaries(limit=3)
        global_summary = generate_global_summary(client, final_messages, previous_summaries)
        store.store_global_summary(global_summary, first_message_id, last_message_id)

        click.secho(f"\nGlobal Summary: {global_summary}", fg=(127, 255, 212))
        click.secho("\nConversation completed successfully", fg="green")

    except Exception as e:
        click.secho(f"Main execution failed: {e}", fg="red")
        raise


if __name__ == "__main__":
    main()
