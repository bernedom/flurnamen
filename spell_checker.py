import sys
import re
import language_tool_python
import os


def correct_text(text, tool):
    matches = tool.check(text)
    corrected_text = language_tool_python.utils.correct(text, matches)
    return corrected_text


def correct_file(filename):
    tool = language_tool_python.LanguageTool('de-CH')

    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split content into lines
    lines = content.split('\n')

    # Identify front matter
    in_front_matter = False
    corrected_lines = []
    for line in lines:
        if line.strip() == '---':
            in_front_matter = not in_front_matter
            corrected_lines.append(line)
            continue

        if in_front_matter:
            corrected_lines.append(line)
            continue

        # Exclude hyperlinks, hyperlink labels, and commented out lines
        if re.match(r'\[.*\]\(.*\)', line) or re.match(r'<!--.*-->', line):
            print(f"Skipping line: {line}")
            corrected_lines.append(line)
            continue

        # Correct the line
        corrected_line = correct_text(line, tool)
        corrected_lines.append(corrected_line)

    # Join corrected lines
    corrected_content = '\n'.join(corrected_lines)

    # Write corrected content back to the file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(corrected_content)


def main():
    if len(sys.argv) != 2:
        print("Usage: python spell_checker.py <markdown_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    if os.path.isdir(file_path):
        for root, dirs, files in os.walk(file_path):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    print(f"Correcting file: {file_path}")
                    correct_file(file_path)
    else:
        correct_file(file_path)



if __name__ == "__main__":
    main()
