import os
import random
import re
from h2ogpte import Session
from config import LLM_ARGS

def ask_llm(session: Session, question: str, llm: str = "gpt-4-1106-preview", llm_args = LLM_ARGS):
    ans = session.query(
        message=question,
        llm=llm,
        llm_args =llm_args,
        rag_config={
            "rag_type": "rag",
        },
    ).content
    return ans

def read_index(index_path):
        """
        Read the index file and return the sections
        """
        sections = []
        with open(index_path, 'r', encoding='utf-8') as index_file:
            for line in index_file:
                section_type, filename = line.strip().split(',')
                sections.append((section_type, filename))
        return sections

def combine_mds(read_path, task_name):
        index_path = os.path.join(read_path, 'index.txt')
        md_path = os.path.join(read_path, 'parts/')
        output_path = os.path.join(read_path, f'{task_name}.md')
        sections = read_index(index_path)

        combined_content = ""
        for section in sections:
            filename = section[1]
            chunk_path = os.path.join(os.path.dirname(md_path), filename)
            with open(chunk_path, 'r', encoding='utf-8') as chunk_file:
                combined_content += chunk_file.read() 

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(combined_content)
        print(f"Combined document saved to {output_path}")
        return combined_content

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
