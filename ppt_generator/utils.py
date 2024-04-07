import os
import random
import re


def read_md_file(file_path, encoding="utf-8"):
    """
    Read the content of a markdown file
    """
    with open(file_path, "r", encoding=encoding) as file:
        content = file.read()
    return content


def save_md(content, save_path):
    """
    Save the content to a markdown file
    """
    with open(save_path, mode="w+", encoding="utf-8") as f:
        f.write(content)


def get_sublist(text):
    """
    Get a list of sublists from a text
    """
    pattern = r"(\d+\.\s.*?)(?=\d+\.|\Z)"
    matches = re.findall(pattern, text, re.DOTALL)
    matches = [i.strip() for i in matches]
    return matches


def get_random_file(path):
    """
    Get a random image file from a folder
    """
    folder_path = path
    files = os.listdir(folder_path)
    random_file = random.choice(files)
    random_file_path = os.path.join(folder_path, random_file)
    return random_file_path
