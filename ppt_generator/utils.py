import os
import random
import re
from h2ogpte import Session
from ppt_generator.config import LLM_ARGS
import json
import Levenshtein

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


def dump_json(data, file_path):
    '''
    Save data in json format
    '''
    with open(file_path, "w") as json_file:
        json.dump(data, json_file)

def read_json(file_path):
    '''
    Load a json object
    '''
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    return data

def extract_text_using_regex(text, pattern):
    matches = re.findall(pattern, text)
    return matches

def generate_ppt_image_mapping(dic_path, md_content, client):
    
    question = '''
                You will receive a markdown file along with a description of an image. Your task is to determine the appropriate section within the markdown file to insert the image, based on the text description and the content of each section. Please provide the name of the section starting with '##', without including any additional text or explanation.
                Markdown file: {}
                Image description: {}
            '''
    
    llm = "h2oai/h2ogpt-4096-llama2-70b-chat"
    ori_dic = read_json(dic_path)
    dic = {}
    pattern = r'##\s*(.*?)(?:\n|$)'

    for key, value in ori_dic.items():
        answer = client.answer_question(llm_args = LLM_ARGS,question= question.format(md_content, value), llm=llm).content
        matches = extract_text_using_regex(answer, pattern)
        if matches:
            section_name = matches[0]
            dic[key] = section_name
    dump_json(dic, 'test.json')
    return dic

def calculate_edit_distance(s1, s2):
  s1, s2 = s1.strip().lower(), s2.strip().lower()
  return Levenshtein.distance(s1, s2)
    

