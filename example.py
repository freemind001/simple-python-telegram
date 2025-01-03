from telegram import Bot
import asyncio
import logging
import json

users = {}


async def sender():
    while True:
        for user_id in users:
            try:
                await bot.send_message(user_id, f"Broadcasted message")
            except Exception as e:
                logging.error(f"Failed to send message to {user_id}: {e}")
        await asyncio.sleep(10)


async def listener():
    async def message_handler(update):
        message = update.get("message")
        if message:
            chat_id = message["chat"]["id"]
            text = message.get("text", "No text provided")
            logging.info(f"New message from {chat_id}: {text}")

            if text == "/start":
                users[chat_id] = {
                    "first_name": message["from"].get("first_name", "Unknown"),
                    "username": message["from"].get("username", "Unknown"),
                    "language_code": message["from"].get("language_code", "Unknown")
                }
                response_text = f"Welcome, {users[chat_id]['first_name']}! You have been added to the users list."
            elif text == "/info":
                response_text = f"Users: {json.dumps(users, indent=2, ensure_ascii=False)}"
            else:
                response_text = f"You said: {text}"

            await bot.send_message(chat_id, response_text)

    await bot.listen(message_handler)


async def main():
    await asyncio.gather(
        sender(),
        listener()
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    API_TOKEN = "your token"
    bot = Bot(API_TOKEN)

    asyncio.run(main())
