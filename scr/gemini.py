import google.generativeai as genai
import os
import typing

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


class Summarizer:
    def __init__(self, api_key: str = API_KEY) -> None:
        self.api_key: str = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def summarize(self, path_text: str, prompt: str) -> str:
        """
        Summarizes the content of the text file based on the provided prompt.

        Args:
            path_text (str): The path to the text file to summarize.
            prompt (str): The prompt to prepend to the text for summarization.

        Returns:
            str: The summarized text.
        """
        if not os.path.exists(path_text):
            raise FileNotFoundError(f"File not found: {path_text}")

        with open(path_text, "r") as file:
            text: str = file.read()

        prompt = prompt + text
        response = self.model.generate_content(prompt)
        return response.to_dict()["candidates"][0]["content"]["parts"][0]["text"]

