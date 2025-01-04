from telegram import Bot
import asyncio
import logging
import json

users = {}


async def sender():
    while True:
        for user_id in users:
            await bot.send_message(user_id, "Broadcasted message")
        await asyncio.sleep(10)


async def listener():
    async def start_command(chat_id, message):
        users[chat_id] = {
            "first_name": message["from"].get("first_name", "Unknown"),
            "username": message["from"].get("username", "Unknown"),
            "language_code": message["from"].get("language_code", "Unknown"),
        }
        response_text = f"Welcome, {users[chat_id]['first_name']}! You have been added to the users list."
        await bot.send_message(chat_id, response_text)

    async def info_command(chat_id, _):
        response_text = f"Users: {json.dumps(users, indent=2, ensure_ascii=False)}"
        await bot.send_message(chat_id, response_text)

    async def default_command(chat_id, message):
        text = message.get("text", "")
        response_text = f"You said: {text}"
        await bot.send_message(chat_id, response_text)

    commands = {
        "/start": start_command,
        "/info": info_command,
    }

    async def dispatch_message(update):
        message = update.get("message")
        if message:
            chat_id = message["chat"]["id"]
            text = message.get("text", "<no text provided>")
            logging.info(f"New message from {chat_id}: {text}")
            command_handler = commands.get(text, default_command)
            await command_handler(chat_id, message)

    await bot.listen(dispatch_message)


async def main():
    await asyncio.gather(
        sender(),
        listener(),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    API_TOKEN = "your token"
    bot = Bot(API_TOKEN)

    asyncio.run(main())
