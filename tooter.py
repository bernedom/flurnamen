import argparse
import re
import os
import mastodon

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Extract and ignore front matter
    front_matter = re.search(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if front_matter:
        front_matter_content = front_matter.group(1)
        content = content[front_matter.end():]
    else:
        front_matter_content = ""

    # Extract thumbnail from front matter
    thumbnail_match = re.search(r'thumbnail:\s*(\S+)', front_matter_content)
    thumbnail = thumbnail_match.group(1) if thumbnail_match else ""

    # Extract title from front matter
    title_match = re.search(r'title:\s*(.+)', front_matter_content)
    title = title_match.group(1) if title_match else ""

    # Remove comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    # Extract paragraphs and link
    paragraphs = content.split('\n\n')
    first_paragraph = paragraphs[0]
    link_match = re.search(r'\[(.*?)\]\((.*?)\)', first_paragraph)
    
    if link_match:
        link_text = link_match.group(1)
        link_url = link_match.group(2)
        first_paragraph = first_paragraph.replace(f'[{link_text}]({link_url})', '...')
    else:
        link_url = ""
    
    remaining_content = '\n\n'.join(paragraphs[1:])

    return first_paragraph, link_url, remaining_content, thumbnail, title

def create_mastodon_post(file_path):
    first_paragraph, link_url, remaining_content, thumbnail, title = parse_markdown(
        file_path)

    post = f"{first_paragraph}\n\n{link_url}\n\n{remaining_content}"
    print("Mastodon Post:")
    print(post)
    if thumbnail:
        print(f"Thumbnail: {thumbnail}")

    if title:
        print(f"Alt Text: Ausschnitt aus Swisstopo, der den Flurnamen {
              title} zeigt.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a Mastodon post from a Markdown file.")
    parser.add_argument("--register-app", action="store_true", help="Register the Mastodon app")
    parser.add_argument("file_path", nargs='?', help="Path to the Markdown file (required unless --register-app is set)")
    args = parser.parse_args()

    if args.register_app:
        # Register the Mastodon app
        mastodon.Mastodon.create_app(
            'flurnamen_client',
            api_base_url='https://tooting.ch',
            to_file='flurnamen_clientcred.secret'
        )
        print("App registered successfully.")
    elif os.path.exists(args.file_path):
        create_mastodon_post(args.file_path)
    else:
        print(f"File {args.file_path} does not exist.")