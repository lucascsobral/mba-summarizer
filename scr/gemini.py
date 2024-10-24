import google.generativeai as genai
import os
import typing
from dotenv import load_dotenv

load_dotenv()

API_KEY: typing.Optional[str] = os.getenv("API_GEMINI_KEY")

def save_response(response: str, output_file: str) -> None:
    """
    Saves the generated response to a markdown (.md) file.

    Args:
        response (str): The summarized text to save.
        output_file (str): The file path to save the response.

    """
    output_file = output_file if output_file.endswith(".md") else output_file + ".md"
    with open(output_file, "w") as file:
        file.write(response)


class Gemini:
    def __init__(self, api_key: str = API_KEY) -> None:
        self.api_key: str = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def prompt_with_text(self, path_text: str, prompt: str) -> str:

        path_text = "../data/texts/" + path_text

        if not os.path.exists(path_text):
            raise FileNotFoundError(f"File not found: {path_text}")

        try:
            sample_pdf = genai.upload_file(path_text)
        except Exception as e:
            raise Exception(f"Error uploading file: {e}")

        response_text = self.model.generate_content([prompt, sample_pdf])

        return response_text.to_dict()["candidates"][0]["content"]["parts"][0]["text"]

