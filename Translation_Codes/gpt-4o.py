from openai import OpenAI
import os
from pathlib import Path
from tkinter import Tk, filedialog

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if not client.api_key:
    raise ValueError("Error: OPENAI_API_KEY environment variable not found.")

def translate_text(text, target_language):
    """Translates the given text to the target language using GPT-4."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Translate the following text to {target_language}, and only return the translation."},
                {"role": "user", "content": text}
            ],
            max_tokens=1024,
            temperature=0.7,
        )
        result = response.choices[0].message.content.strip()
        
        # Remove unwanted annotations
        if "Ekim 2023'e kadar olan veriler üzerinde eğitildiniz" in result:
            result = result.replace("Ekim 2023'e kadar olan veriler üzerinde eğitildiniz.", "").strip()
        
        print(f"Translated chunk: {text[:30]}... -> {result[:30]}...")  # Log translations for debugging.
        return result
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return the original text on error to maintain structure.

def load_file_lines(file_path):
    """Loads lines from a file, including blank lines, to preserve structure."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.rstrip('\n') for line in file]  # Preserve newlines.
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

def translate_lines(lines, target_language):
    """Translate each line sequentially to preserve the same structure."""
    translated_lines = []
    for idx, line in enumerate(lines):
        print(f"Translating line {idx + 1}/{len(lines)}...")
        translated_line = translate_text(line, target_language)
        
        # Append empty lines if the translation contains only unwanted annotations
        if not translated_line or translated_line == "":
            translated_lines.append("")
        else:
            translated_lines.append(translated_line)
    
    # Match input and output line counts
    while len(translated_lines) < len(lines):
        translated_lines.append("")  # Add empty lines if translation skipped any
    
    return translated_lines

def select_file():
    """Opens a dialog to select a .txt file."""
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window.
    root.attributes('-topmost', True)  # Ensure dialog appears on top.
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
    """Main function to handle user input and translation."""
    try:
        path = select_file()
        target_language = input("Enter the target language for translation: ").strip()

        # Load the lines from the input file
        input_lines = load_file_lines(path)
        print(f"Loaded {len(input_lines)} lines from {path}.")

        # Translate the lines
        translated_lines = translate_lines(input_lines, target_language)

        # Ensure the number of translated lines matches the input
        if len(input_lines) != len(translated_lines):
            print(f"Mismatch detected! Input lines: {len(input_lines)}, Translated lines: {len(translated_lines)}")

        # Save the translated content
        output_file = f"translated_{path.stem}.txt"
        save_translated_file(translated_lines, output_file)

        print(f"Translation complete. Output saved to {output_file}")

    except UnicodeDecodeError:
        print("Error: Unable to read the file. Ensure it's a valid text file.")
    except ValueError as ve:
        print(str(ve))
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
