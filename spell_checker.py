import sys
import re
import language_tool_python


def correct_text(text, tool):
    matches = tool.check(text)
    corrected_text = language_tool_python.utils.correct(text, matches)
    return corrected_text


def main():
    if len(sys.argv) != 2:
        print("Usage: python spell_checker.py <markdown_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    tool = language_tool_python.LanguageTool('de-CH')

    with open(file_path, 'r', encoding='utf-8') as file:
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

        # Exclude hyperlinks and hyperlink labels
        if re.match(r'\[.*\]\(.*\)', line):
            corrected_lines.append(line)
            continue

        # Correct the line
        corrected_line = correct_text(line, tool)
        corrected_lines.append(corrected_line)

    # Join corrected lines
    corrected_content = '\n'.join(corrected_lines)

    # Write corrected content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(corrected_content)


if __name__ == "__main__":
    main()
