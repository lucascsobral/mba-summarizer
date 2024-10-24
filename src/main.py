import time
from http.client import responses
from lib2to3.fixes.fix_input import context

from scraper import scraper_main
from downloader import download_video
from fragmenter import fragment_audio
from transcriber import transcribe_audios
from google_drive_service import GoogleDriveManager, FOLDER_ID, SCOPES, SERVICE_ACCOUNT_FILE
from gemini import Gemini, save_response
from discord_sender import DiscordSender
from utils import format_string
import asyncio
import json
import os
from dotenv import load_dotenv
from typing import List, Dict
from discord import File
from datetime import datetime, timedelta


NOTES_NAMES = ["summarize",
               "relevant_topics",
               "jargons",
               "references",
               "reference_relevant_topics"
               ]

# 1 - Step Scraper
def scraper():
    link, class_name = asyncio.run(scraper_main())

    return link, class_name

# 2 - Download the file

def download_file(link):
    try:
        download_video(link)
        return True
    except Exception as e:
        print(f"Erro ao baixar o vídeo: {e}")
        return False

# 3 - Fragment the audio
def fragment(input_file, output_folder, segment_duration=150):
    try:
        fragment_audio(input_file, output_folder, segment_duration)
        return True
    except Exception as e:
        print(f"Erro ao fragmentar o áudio: {e}")
        return False


# 4 - Transcribe the audio
def transcribe():
    try:
        transcribe_audios("../data/fragments/")
        return True
    except Exception as e:
        print(f"Erro ao transcrever o áudio: {e}")
        return False

# 4.1 - Create the folder class in Google Drive

def create_new_folder(class_name):
    gd = GoogleDriveManager(SERVICE_ACCOUNT_FILE, SCOPES)

    folder_number = gd.list_folders_in_folder(FOLDER_ID)
    folder_name = format_string(class_name)
    folder_id = gd.create_formatted_folder(folder_name, folder_number, FOLDER_ID)

    return folder_id


# 4.2 - Save the transcription in Google Drive
def save_in_google_drive(file_name, file_path: str, folder_id: str) -> None:
    file_name = file_name.split(".")[0]
    gd = GoogleDriveManager(SERVICE_ACCOUNT_FILE, SCOPES)
    gd.upload_file_to_folder(file_name, file_path, folder_id)

#:TODO 5 - Summarize,  the transcription
class UseGemini:
    def __init__(self):
        self.gemini = Gemini()
        with open("../data/config_prompt.json", "r") as file:
            self.config_prompt = json.load(file)

    def create_notes(self, file_path: str, output_file: str, prompt: str):
        response = self.gemini.prompt_with_text(file_path, prompt)
        save_response(response, "../data/texts/" + output_file)

    def create_class_theme(self, file_path: str) -> str:
        response = self.gemini.prompt_with_text(
            file_path,
            "De forma sucinta, qual o tema da aula? A resposta deve conter no máximo 3 linhas."
        )
        return response

#:TODO 7 - Send the notes to Discord

def format_message(date: str, class_name: str, theme: str) -> str:
    message = f"""
Matéria: {class_name}
Data da aula: {date}
Tema da Aula: {theme}
Resumo: Anexos
    """
    return message


def send_to_discord(list_files: List[str], message: str):
    dcs = DiscordSender()
    # Load the notes
    opened_files: List[File] = dcs.open_files(list_files)

    dcs.mess_with_files(
        content=message,
        files=opened_files
    )

def app():
    # 1 - Step Scraper
    load_dotenv()
    link, class_name = scraper()
    print(link, class_name)
    # 2 - Download the file
    download_file(link)
    # 3 - Fragment the audio
    fragment("../data/audio/video.wav", "../data/fragments/")
    # 4 - Transcribe the audio
    transcribe()
    # 4.1 - Create the folder class in Google Drive
    folder_id = create_new_folder(class_name)
    # 4.2 - Save the transcription in Google Drive
    save_in_google_drive("transcription.txt","../data/texts/transcription.txt", folder_id)
    # 5 - Generate the notes from the transcription
    gemini = UseGemini()
    path_texts_list: List[str] = []
    for note in NOTES_NAMES:
        print(f"Creating note: {note}")
        gemini.create_notes(
            gemini.config_prompt[note]["origin_file"],
            gemini.config_prompt[note]["file_name"],
            gemini.config_prompt[note]["prompt"]
        )
        print(f"Created note: {note}")
        # 6 - Save the notes in Google Drive
        save_in_google_drive(
            gemini.config_prompt[note]["file_name_pt"],
            f"../data/texts/{gemini.config_prompt[note]['file_name']}",
            folder_id
        )
        path_texts_list.append(f"../data/texts/{gemini.config_prompt[note]['file_name']}")
        print(f"Saved note on Google Drive: {note}")
        time.sleep(60)
    # 7 - Send the notes to Discord
    class_theme = gemini.create_class_theme("transcription.txt")
    class_date = datetime.now() - timedelta(days=1)
    message = format_message(
        class_date.strftime("%d/%m/%Y"),
        class_name,
        class_theme
    )

    send_to_discord(path_texts_list, message)

    # Delete the files from the text folder
    for file in path_texts_list:
        os.remove(file)

    # return a message in CLI in format json to be used in N8N (Temporarily)
    return json.dumps({
        "class_name": class_name,
        "class_date": class_date.strftime("%d/%m/%Y"),
        "class_theme": class_theme
    })


if __name__ == "__main__":
    app()
