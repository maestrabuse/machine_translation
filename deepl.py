import requests
from pathlib import Path
from tkinter import Tk, filedialog

DEEPL_API_KEY = "8ed6f659-b9fd-4e1d-b332-d9304a51788d"  # Pro API Key

def translate_text_deepl(text, target_language):
    """Translates the given text to the target language using DeepL API."""
    try:
        response = requests.post(
            "https://api.deepl.com/v2/translate",  # Correct endpoint for Pro API
            data={
                "auth_key": DEEPL_API_KEY,
                "text": text,
                "target_lang": target_language.upper()
            },
        )

        if response.status_code != 200:
            print(f"API Error: {response.status_code} - {response.text}")
            return text  # Return original text on error.

        result = response.json()

        if 'translations' not in result:
            print(f"Unexpected API response: {result}")
            return text  # Return original text on error.

        translated_text = result['translations'][0]['text']
        print(f"Translated chunk: {text[:30]}... -> {translated_text[:30]}...")
        return translated_text

    except Exception as e:
        print(f"DeepL Translation error: {e}")
        return text  # Return original text on error.

def load_file_lines(file_path):
    """Loads lines from a file, including blank lines, to preserve structure."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.rstrip('\n') for line in file]
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

def translate_lines_deepl(lines, target_language):
    """Translate each line using the DeepL API."""
    translated_lines = []
    for idx, line in enumerate(lines):
        print(f"Translating line {idx + 1}/{len(lines)}...")
        translated_line = translate_text_deepl(line, target_language)
        translated_lines.append(translated_line if translated_line else "")
    return translated_lines

def select_file():
    """Opens a dialog to select a .txt file."""
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
    with open(output_file, 'w', encoding='utf-8') as file:
        for line in translated_lines:
            file.write(line + '\n')

def main():
    """Main function to handle user input and translation using DeepL."""
    try:
        path = select_file()
        target_language = input("Enter the target language for translation (e.g., EN, DE, FR): ").strip().upper()

        input_lines = load_file_lines(path)
        print(f"Loaded {len(input_lines)} lines from {path}.")

        translated_lines = translate_lines_deepl(input_lines, target_language)

        if len(input_lines) != len(translated_lines):
            print(f"Mismatch detected! Input lines: {len(input_lines)}, Translated lines: {len(translated_lines)}")

        output_file = f"translated_{path.stem}.txt"
        save_translated_file(translated_lines, output_file)

        print(f"Translation complete. Output saved to {output_file}")

    except UnicodeDecodeError:
        print("Error: Unable to read the file. Ensure it's a valid text file.")
    except ValueError as ve:
        print(str(ve))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()