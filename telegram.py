import httpx
import asyncio
import logging


class Bot:
    """
    A class that interacts with Telegram Bot API to send and receive messages.

    Methods:
        listen: Starts listening for messages and handles them using the provided message handler.
        send_message: Sends a message to a specified chat.
    """

    def __init__(self, token: str):
        self.base_url = f"https://api.telegram.org/bot{token}"
        self._message_handler = None
        self._offset = None
        self._processing_delay = 1

    async def _process_updates(self):
        try:
            params = {"timeout": 30}
            if self._offset:
                params["offset"] = self._offset

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/getUpdates",
                    params=params,
                    timeout=params['timeout'] + 10
                )
                response.raise_for_status()
                updates = response.json()
                if updates.get("ok") and "result" in updates:
                    for update in updates["result"]:
                        if self._message_handler:
                            await self._message_handler(update)
                        self._offset = update["update_id"] + 1
                return updates
        except Exception as e:
            logging.error(f"Error processing updates: {str(e)}")
            return {"ok": False, "error": str(e)}

    async def listen(self, message_handler):
        """
        Starts the bot's listening loop and processes incoming messages using the provided handler.

        Args:
            message_handler (callable): The function to handle incoming messages.

        This method continuously checks for updates and calls the provided `message_handler`
        function to process them. If there is an error, it will retry with increasing delay.
        """
        self._message_handler = message_handler
        while True:
            result = await self._process_updates()
            if not result.get("ok"):
                self._processing_delay = min(self._processing_delay * 2, 60)
                logging.info(f"Waiting for {self._processing_delay} seconds.")
                await asyncio.sleep(self._processing_delay)
            else:
                self._processing_delay = 1

    async def send_message(self, chat_id: int, text: str):
        """
        Sends a message to the specified chat.

        Args:
            chat_id (int): The unique identifier for the target chat.
            text (str): The text of the message to send.

        Returns:
            dict: The response from the Telegram API.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={"chat_id": chat_id, "text": text}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logging.error(f"Error sending message to {chat_id}: {str(e)}")
            return {"ok": False, "error": str(e)}