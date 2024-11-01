import requests
import uuid
import json
from pathlib import Path
from tkinter import Tk, filedialog

# Azure Translator API credentials
AZURE_TRANSLATOR_KEY = "9fe3031050fa4941a7f5b831be2a5aad"
AZURE_ENDPOINT = "https://api.cognitive.microsofttranslator.com"
AZURE_REGION = "eastus"  # Replace with the region of your resource

def translate_text_azure(text, target_language):
    """Translate text using Azure Translator Text API."""
    path = "/translate?api-version=3.0"
    params = f"&to={target_language}"
    constructed_url = AZURE_ENDPOINT + path + params

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_REGION,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    body = [{"text": text}]

    try:
        response = requests.post(constructed_url, headers=headers, json=body)

        if response.status_code != 200:
            print(f"API Error: {response.status_code} - {response.text}")
            return text  # Return original text on error.

        result = response.json()
        translated_text = result[0]["translations"][0]["text"]
        print(f"Translated chunk: {text[:30]}... -> {translated_text[:30]}...")
        return translated_text

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return text  # Return original text on error.

def load_file_lines(file_path):
    """Load lines from a file, including blank lines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.rstrip('\n') for line in file]
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

def translate_lines_azure(lines, target_language):
    """Translate each line using Azure Translator Text API."""
    translated_lines = []
    for idx, line in enumerate(lines):
        print(f"Translating line {idx + 1}/{len(lines)}...")
        translated_line = translate_text_azure(line, target_language)
        translated_lines.append(translated_line if translated_line else "")
    return translated_lines

def select_file():
    """Open a dialog to select a .txt file."""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(
        title="Select a Text File",
        filetypes=[("Text Files", "*.txt")]
    )
    if not file_path:
        raise ValueError("No file selected. Exiting...")
    return Path(file_path)

def save_translated_file(translated_lines, output_file):
    """Save translated lines to the output file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            for line in translated_lines:
                file.write(line + '\n')
        print(f"Translation saved successfully to {output_file}")
    except Exception as e:
        print(f"Error saving the file: {e}")

def main():
    """Main function to handle user input and translation using Azure."""
    try:
        path = select_file()
        target_language = input("Enter the target language (e.g., en, de, fr): ").strip()

        # Load lines from the input file
        input_lines = load_file_lines(path)
        if not input_lines:
            print("The selected file is empty or could not be read.")
            return

        print(f"Loaded {len(input_lines)} lines from {path}.")

        # Translate lines using Azure API
        translated_lines = translate_lines_azure(input_lines, target_language)

        if len(input_lines) != len(translated_lines):
            print(f"Mismatch detected! Input lines: {len(input_lines)}, Translated lines: {len(translated_lines)}")

        # Save the translated content
        output_file = f"translated_{path.stem}.txt"
        save_translated_file(translated_lines, output_file)

    except UnicodeDecodeError:
        print("Error: Unable to read the file. Ensure it's a valid text file.")
    except ValueError as ve:
        print(str(ve))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
