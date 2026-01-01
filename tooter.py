import argparse
import re
import os
import mastodon
import datetime
import shutil
from glob import glob

def replace_links_with_ellipsis(text, only_extract=False):
    link_match = re.search(r'!?\[(.*?)\]\((.*?)\)', text)
    if link_match:
        link_text = link_match.group(1)
        link_url = link_match.group(2)
        if not only_extract:
            text = text.replace(f'[{link_text}]({link_url})', '...')
    else:
        link_url = ""
        link_text = ""

    return text, link_url, link_text

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
    
    return paragraphs, thumbnail, title

def create_stub(flurname, url, folder='./docs/_posts'):

    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)

    # Replace spaces with dashes in flurname
    
    flurname_slug = flurname.replace(' ', '-').lower()
    flurname_slug = flurname_slug.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')

    # Create a filename based on the current date and flurname
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f"{date_str}-{flurname_slug}.md"
    file_path = os.path.join(folder, filename)

    # Create the content for the stub
    content = f"""---
title: "{flurname}"
layout: post
thumbnail: images/{flurname_slug}.png
excerpt_separator: <!--more-->
---

Lorem Ipsum [{flurname}]({url}).

Bla Ba

<!--more-->
"""

    # Write the content to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f"Stub created at {file_path}")
    return flurname_slug

def copy_screenshot(flurname, screenshotfolder=os.path.expanduser('~/Pictures/Screenshots'), targetfolder='./docs/images'):
    # Ensure the target folder exists
    os.makedirs(targetfolder, exist_ok=True)

    # Get today's date in the screenshot format
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    pattern = os.path.join(screenshotfolder, f"Screenshot from {date_str} *.png")
    screenshots = glob(pattern)

    if not screenshots:
        print(f"No screenshot found for today ({date_str}) in {screenshotfolder}")
        return None

    # Use the most recent screenshot if multiple found
    latest_screenshot = max(screenshots, key=os.path.getctime)
    target_path = os.path.join(targetfolder, f"{flurname.replace(' ', '-').lower()}.png")
    shutil.copy2(latest_screenshot, target_path)
    print(f"Copied screenshot to {target_path}")
    return target_path


def create_mastodon_post(file_path):
    paragraphs, thumbnail, title = parse_markdown(
        file_path)

    first_paragraph, link_url = replace_links_with_ellipsis(paragraphs[0])
    remaining_content = '\n\n'.join(paragraphs[1:])
    post = f"{first_paragraph}\n\n{link_url}\n\n{remaining_content}"
    print("Mastodon Post:")
    print(post)
    if thumbnail:
        print(f"Thumbnail: {thumbnail}")

    alt_text = f"Ausschnitt aus Swisstopo, der den Flurnamen {title} zeigt."
    if title:
        print(f"Alt Text: Ausschnitt aus Swisstopo, der den Flurnamen {
              title} zeigt.")
        
    return (post, thumbnail, alt_text)

def create_mastodon_story(file_path):
    paragraphs, thumbnail, title = parse_markdown(
        file_path)

    first_paragraph, link_url, link_text = replace_links_with_ellipsis(paragraphs[0])
    
    story_head = f"{first_paragraph}\n\n{link_url}\n\n{paragraphs[1]}"
    print("Mastodon Story:")
    print(story_head)
    
    if thumbnail:
        print(f"Thumbnail: {thumbnail}")

    alt_text = f"Ausschnitt aus Swisstopo, der den Flurnamen {title} zeigt."
    if title:
        print(f"Alt Text: Ausschnitt aus Swisstopo, der den Flurnamen {
              title} zeigt.")
        
    for para in paragraphs[2:]:
        cleaned_para, link, link_text = replace_links_with_ellipsis(para, only_extract=True)
        
        print("\n--- Next Story Part ---\n")
        print(cleaned_para)
        if link:
            print(f"\nLink: {link}\n")
        if link_text:
            print(f"Link Text: {link_text}")

        
    return (story_head, thumbnail, alt_text)        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a Mastodon post from a Markdown file.")
    parser.add_argument("--register-app", action="store_true", help="Register the Mastodon app")
    parser.add_argument("--login", action="store_true", help="Log in to Mastodon")
    parser.add_argument("file_path", nargs='?', help="Path to the Markdown file (required unless --register-app or --login is set)")
    parser.add_argument("--create", help="Create a new stub for a post pass the flurname")
    parser.add_argument("--url", help="URL for the new stub")
    parser.add_argument("--post", action="store_true", help="if set the post will be posted to mastodon")
    parser.add_argument("--story", action="store_true", help="Create a story post instead of a regular post")

    args = parser.parse_args()

    if not args.register_app and not args.login and not args.file_path and not args.create:
        parser.error("the following arguments are required: file_path")
    
    if args.create:
            
        url = "https://draeckgaden.ch"
        if args.url:
            url = args.url
        flurname = create_stub(args.create, url)
        copy_screenshot(flurname)

    elif args.register_app:
        # Register the Mastodon app
        mastodon.Mastodon.create_app(
            'flurnamen_client',
            api_base_url='https://tooting.ch',
            to_file='flurnamen_clientcred.secret'
        )
        print("App registered successfully.")
    elif args.login:
        
        mastodon_instance = mastodon.Mastodon(
            client_id='flurnamen_clientcred.secret',
            api_base_url='https://tooting.ch'
        )
        
        print(mastodon_instance.auth_request_url())

        mastodon_instance.log_in(
            code = input("Enter the code from the URL: "),
            to_file='flurnamen_usercred.secret'
        )
        print("Logged in successfully.")
    elif os.path.exists(args.file_path):
        
        mastodon_instance = mastodon.Mastodon(
            client_id='flurnamen_clientcred.secret',
            access_token='flurnamen_usercred.secret',
            api_base_url='https://tooting.ch'
        )

        if args.post:
            (post, thumbnail, alt) = create_mastodon_post(args.file_path)
            thumbnail_path = os.path.join('docs', thumbnail)
            if len(post) > 500:
                print(f"Warning: Post exceeds 500 characters ({len(post)} characters) and will not be posted to Mastodon.")
            else:
                
                print("Posting image to mastodon")
                media = mastodon_instance.media_post(thumbnail_path, description=alt)
                print("Posting text to mastodon")
                status = mastodon_instance.status_post(post, media_ids=media)
                print(f"Post created successfully: {status.url} ({status.id})")
        elif args.story:
            (story, thumbnail, alt) = create_mastodon_story(args.file_path)
            

            
    else:
        print(f"File {args.file_path} does not exist.")