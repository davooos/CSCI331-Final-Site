import os
import json
from groq import Groq


def load_hot_tubs_data():
    json_path = os.path.join("static", "hot_tubs.json")
    with open(json_path, "r") as file:
        hot_tubs = json.load(file)
    return hot_tubs


class Chat:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.hot_tubs_data = load_hot_tubs_data()  # <-- your JSON here

        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a chat bot sales rep that sells hot tubs. "
                    "You give short, concise answers no longer than 50 words. "
                    "Don't style the text in any way. Your name is Tubby."
                    "Start by introducing yourself and convince the customer to buy a hot tub. "
                    "Do not ever let the topic go away from hot tubs. "
                    "Do not use text formatting or special symbols, the chats are displayed directly in a text bubble. "
                    "Always ask questions to engage the customer. "
                    "Use the provided hot tub catalog when recommending products."
                ),
            },
            # Optional: first assistant line (you already had this)
            {
                "role": "assistant",
                "content": "Hello! What is your name?",
            },
        ]

    def send_message(self, input_text: str):
        # Add the catalog as an extra system message each call
        catalog_str = json.dumps(self.hot_tubs_data)

        completion = self.client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=self.messages + [
                {
                    "role": "system",
                    "content": (
                        "Here is the current hot tub catalog in JSON. "
                        "Use this data to answer questions and recommend specific models:\n"
                        f"{catalog_str}"
                    ),
                },
                {
                    "role": "user",
                    "content": input_text,
                },
            ],
            stream=True,
            temperature=0.5,
        )

        # Remember the user message in the conversation history
        self.messages.append({"role": "user", "content": input_text})
        return completion


class Message:
    def __init__(self, sender, content):
        self.sender = sender
        self.content = content
        self.length = len(content)


def main():  # CLI chat interface for testing
    chat = Chat()
    print("Hello! What is your name?")
    while True:
        user_query = input("\nYou: ")

        # Collect the streamed chunks into one assistant message
        assistant_reply = ""
        for chunk in chat.send_message(user_query):
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            assistant_reply += delta

        # Store the full assistant message once
        chat.messages.append({"role": "assistant", "content": assistant_reply})


if __name__ == "__main__":
    main()
