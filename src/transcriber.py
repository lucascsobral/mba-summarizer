import speech_recognition as sr
import os
from typing import List, Optional


def transcribe_audios(
        audio_folder_path: str,
        output_file: str = "../data/texts/transcription.txt",
        max_attempts: int = 3,
        language: str = "pt-BR"
) -> Optional[str]:
    """
    Transcribes audio files from the specified folder and saves the transcription to an output file.

    Args:
        audio_folder_path (str): Path to the folder containing the audio files.
        output_file (str): Name of the file where the transcription will be saved. Default: "transcription.txt".
        max_attempts (int): Maximum number of speech recognition attempts per file. Default: 3.
        language (str): Language code for the speech recognition service. Default: "pt-BR".

    Returns:
        Optional[str]: Returns the complete transcription as a string or None if an error occurs.
    """

    # Initialize the speech recognizer
    recognizer = sr.Recognizer()

    # Filter audio files (e.g., only .wav files)
    audio_files: List[str] = [f for f in os.listdir(audio_folder_path) if f.endswith(".wav")]
    audio_files.sort()

    if not audio_files:
        print("No audio files found.")
        return None

    text_transcriptions: List[str] = []

    # Loop through the audio files
    for audio_name in audio_files:
        print(f"Processing: {audio_name}")
        audio_file_path = os.path.join(audio_folder_path, audio_name)
        # Using a file context manager to ensure the file is closed properly
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)  # Read the audio

        # Recognition attempts
        for attempt in range(max_attempts):
            try:
                # Transcribing the audio
                text = recognizer.recognize_google(audio_data, language=language)
                # Adding the transcription to the list
                text_transcriptions.append(text + " ")
                break  # Success, exit the attempt loop
            except sr.UnknownValueError:
                print(f"Attempt {attempt + 1}/{max_attempts}: Could not understand the audio: {audio_name}")
            except sr.RequestError as e:
                print(
                    f"Attempt {attempt + 1}/{max_attempts}: Error requesting the speech recognition service for {audio_name}; {e}")

        else:
            print(f"Failed to transcribe {audio_name} after {max_attempts} attempts.")

    # Check if any transcriptions were made
    if not text_transcriptions:
        print("No transcriptions made.")
        return None

    # Combine all transcriptions into one text
    final_text = "".join(text_transcriptions)

    # Save the text to a file
    with open(output_file, "w") as file:
        file.write(final_text)

    return final_text