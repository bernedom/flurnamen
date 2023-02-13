from textparser import *

if __main__:  # This is the main program
    # Create a new TextParser object
    parser = TextParser()
    # Parse the text file
    parser.parse("text.txt")
    # Print the parsed text
    print(parser.get_text())
