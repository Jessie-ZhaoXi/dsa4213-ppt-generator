from typing import Optional

from h2ogpte import Session
from utils import get_sublist, save_md
from config import LLM_ARGS
from utils import *
import os
import re

class MarkdownGenerator:
    def __init__(self, session, markdown_path):
        self.session = session


    def _revise_title_name(self, markdown_text: str, opinion: str, main_idea: str, language: str = "English") -> str:
        # Extract the current title from the markdown text using regex
        pattern = r"^#\s(.+)$"
        match = re.search(pattern, markdown_text, re.MULTILINE)
        if match:
            current_title = match.group(1)
        else:
            # Handle case where no title is found
            current_title = "No title found"
            print(current_title)
            return current_title

        # Construct the prompt to revise the title based on the main idea and the provided opinion
        prompt = f"""
        You are a "title revisor" and you can refine titles based on provided feedback. No matter what the input language is, you must output text in {language}.
        Given the current title "{current_title}" and the central theme "{main_idea}", along with this feedback: "{opinion}", please refine the title to better reflect the central theme and feedback. Please keep the response to no more than 15 words.
        """
        
        revised_title = ask_llm(self.session, prompt)
        return revised_title
    
    def _revise_introduction(self, markdown_text: str, main_idea: str, opinion: str, character_a: str, language: str = "English") -> str:
        # Regular expression to extract the introduction section from the markdown content
        pattern = r"\n## Introduction\n\n([\s\S]+?)(?=\n##|$)"
        match = re.search(pattern, markdown_text)

        if match:
            current_introduction = match.group(1).strip()  # Capture the introduction content and strip any extra whitespace
        else:
            # If no introduction is found
            print("No introduction found in the markdown text.")
            return "No introduction found in the markdown text."

        # Construct the prompt to revise the introduction based on the main idea and the opinion provided
        prompt = f"""
        You are a {character_a}, tasked with revising an introduction based on a specific central theme and specific feedback. The current introduction reads:
        "{current_introduction}"
        Based on the central theme "{main_idea}" and the following opinion "{opinion}", please revise this introduction. Ensure the language used matches the {language} language requirements. The revision should be concise, informative, reflecting expertise in the field, and should guide the full text. Aim for a length of about 200 words.
        """

        # Use the LLM to generate a revised introduction
        revised_introduction = ask_llm(self.session, prompt)
        return revised_introduction
    
    def _revise_sub_content(self, markdown_text: str, opinion: str, task_name: str, main_idea: str, character_a: str, language: str = "English") -> str:
        # Regular expression to extract the sub-idea and its content
        # Assumes there might be multiple sub-ideas and contents, so we focus on the first match
        pattern = r"\n\n## ([^\n]+)\n\n([\s\S]+?)(?=\n## |\Z)"
        match = re.search(pattern, markdown_text)

        if match:
            sub_idea_i = match.group(1).strip()  # Capture the sub-idea
            sub_content = match.group(2).strip()  # Capture the sub-content immediately following the sub-idea
            print("sub_idea_i is \n", sub_idea_i)
            print("sub_content is \n", sub_content)
        else:
            # If no sub-idea or sub-content is found
            print("No sub-section found in the markdown text.")
            return "No sub-section found in the markdown text."

        # Construct the prompt to revise the sub-content based on the sub-idea, main idea, and provided opinion
        prompt = f"""
        You are a {character_a}, tasked with revising the content of a sub-section based on feedback and the central theme of a document. The sub-idea is titled "{sub_idea_i}" and the current content reads:
        "{sub_content}"
        Based on the central theme "{main_idea}", the task name "{task_name}", and the following specific opinion "{opinion}", please revise this sub-section. Ensure the language used is {language} and that the revision is insightful, detailed, and aligns with the overall document. The revision should also facilitate a deeper understanding of the sub-idea, and you shall only return the revised content of this sub-section, do not include the sub-idea.
        """

        # Use the LLM to generate revised sub-content
        revised_sub_content = ask_llm(self.session, prompt)
        return [sub_idea_i, revised_sub_content]

    def _revise_end_sentence(self, markdown_text: str, opinion: str, task_name: str, main_idea: str, character_a: str, language: str = "English") -> str:
        # Regular expression to extract the conclusion section from the markdown content
        pattern = r"\n\n## Conclusion\n\n([\s\S]+)"
        match = re.search(pattern, markdown_text)

        if match:
            end_sentence = match.group(1).strip()  # Capture the conclusion content
        else:
            # If no conclusion is found
            print("No conclusion section found in the markdown text.")
            return "No conclusion section found in the markdown text."

        # Construct the prompt to revise the end sentence based on the main idea, task name, and provided opinion
        prompt = f"""
        You are a {character_a}, tasked with revising the conclusion of a document. The current conclusion reads:
        "{end_sentence}"
        Based on the central theme "{main_idea}", the task name "{task_name}", and the following specific opinion "{opinion}", please revise this conclusion. Ensure the language used is {language}, and that the revision succinctly encapsulates the main findings or arguments and reflects upon the implications or future directions. The revision should be clear, compelling, and concise.
        """

        # Use the LLM to generate a revised conclusion
        revised_end_sentence = ask_llm(self.session, prompt)
        return revised_end_sentence

    
    def _revise_md(self, read_path, page:int, opinion:str, 
        character_a: str = "you are a professional researcher"):
        """
        Revise the markdown content.
        """
        # Preparation work
        index_path = os.path.join(read_path, 'index.txt')
        md_path = os.path.join(read_path, 'parts/')
        sections = read_index(index_path)
        task_name = "write a summary"

        article_summary = self.main_idea_knowledge

        # Get the main idea
        main_idea = self._get_main_idea(
            task_name, character_a, knowledge_content=article_summary
        )

        task_name = "revise the content based on the feedback"
        
        section = sections[page - 1]
        section_type, filename = section

        chunk_path = os.path.join(os.path.dirname(md_path), filename)
        with open(chunk_path, 'r', encoding='utf-8') as chunk_file:
            markdown_text = chunk_file.read() 
        
        if section_type == "title":
            new_title = self._revise_title_name(markdown_text, opinion, main_idea)
            save_md("# " + new_title + "\n", chunk_path)
            
        elif section_type == "introduction":
            new_intro = self._revise_introduction(markdown_text, main_idea, opinion, character_a)
            save_md("\n## Introduction\n\n" + new_intro, chunk_path)

        elif section_type == "subsection":
            sub_idea_i, new_sub_content = self._revise_sub_content(markdown_text, opinion, task_name, main_idea, character_a)
            save_md("\n\n## " + sub_idea_i + "\n\n" + new_sub_content , chunk_path)

        else:
            new_end_sentence = self._revise_end_sentence(markdown_text, opinion, task_name, main_idea, character_a)
            save_md("\n\n## Conclusion\n\n" + new_end_sentence, chunk_path)

    def _delete_md(self, read_path, page:int):
        """
        Delete the markdown content, and update the index file
        """
        index_path = os.path.join(read_path, 'index.txt')
        md_path = os.path.join(read_path, 'parts/')
        sections = read_index(index_path)
        section = sections[page - 1]
        section_type, filename = section

        chunk_path = os.path.join(os.path.dirname(md_path), filename)
        os.remove(chunk_path)
        sections.pop(page - 1)

        with open(index_path, 'w', encoding='utf-8') as index_file:
            for section in sections:
                section_type, filename = section
                index_file.write(section_type + "," + filename + '\n')

    def update_md(self, path, opinion):
        """
        Update the markdown content.
        first step ask llm to parse opinions into three categories : revise/delete/regenrate the content based on the feedback.
        then call the respective function to update the content.
        """