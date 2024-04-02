import os
import random
import re


def save_md(content, save_path):
    with open(save_path, mode="w+", encoding="utf-8") as f:
        f.write(content)


def get_sublist(text):
    pattern = r"(\d+\.\s.*?)(?=\d+\.|\Z)"
    matches = re.findall(pattern, text, re.DOTALL)
    matches = [i.strip() for i in matches]
    return matches