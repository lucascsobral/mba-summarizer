from discord import SyncWebhook, File
from typing import List
import os
from dotenv import load_dotenv


WEBHOOK_URL = os.getenv("WEBHOOK_URL_DISCORD")


class DiscordSender:
    def __init__(self, webhook_url=WEBHOOK_URL):
        self.webhook = SyncWebhook.from_url(webhook_url)

    def mess_with_files(self, content: str, files: List[File]):
        self.webhook.send(content=content, files=files)

    @staticmethod
    def open_files(list_files: List[str]) -> List[File]:
        files_contents: List[File] = []

        for file_path in list_files:
            files_contents.append(File(file_path, filename=file_path.split("/")[-1]))

        return files_contents