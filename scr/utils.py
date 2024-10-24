
def format_string(text: str) -> str:
    # Convert the string to lowercase
    formatted_text = text.lower()
    # Replace spaces with hyphens
    formatted_text = formatted_text.replace(' ', '-')
    return formatted_text