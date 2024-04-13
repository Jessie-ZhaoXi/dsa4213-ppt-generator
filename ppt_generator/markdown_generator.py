from typing import Optional

from h2ogpte import Session
from utils import get_sublist, save_md
from config import LLM_ARGS
from utils import *
import os


class MarkdownGenerator:

    def __init__(
        self,
        session: Session,
        min_sub_idea_num: int = 2,
        max_sub_idea_num: int = 6,
        **kwargs,
    ):
        """
        Initializes the MarkdownGenerator object.

        Args:
            session (Session): The H2OGPTE session object.
            min_sub_idea_num (int): The minimum number of sub-ideas to generate. Defaults to 2.
            max_sub_idea_num (int): The maximum number of sub-ideas to generate. Defaults to 5.
            **kwargs: Additional keyword arguments.

        """
        self.session = session
        self.min_sub_idea_num = min_sub_idea_num
        self.max_sub_idea_num = max_sub_idea_num
        if kwargs.get("main_idea_knowledge"):
            self.main_idea_knowledge = kwargs["main_idea_knowledge"]
        else:
            self.main_idea_knowledge = " "

# ==============================================================================
# markdown generator(internal use)
# ==============================================================================
    def _get_main_idea(
        self,
        task_name: str,
        character_a: str,
        language: str = "English",
        knowledge_content: Optional[str] = None,
        instruction: Optional[str] = None,
    ) -> str:
        """
        Generates the main idea of the article based on the given task name, character, reference content, and optionally user-defined instruction. The LLM decides if the instruction is relevant and follows it accordingly.
        """

        # Include the instruction in the prompt and conditionally apply it based on its relevance
        instruction_text = f"If relevant, consider the following user instruction: '{instruction}'. Otherwise, ignore it." if instruction else "There is no specific user instruction."
        
        prompt = f"""You are a {character_a}. You can generate specific central themes based on a task. No matter what the input language is, you must output text in {language}.
        There is a task "{task_name}". Please generate the main idea of the article of this task type based on the reference content of the uploaded PDF I gave you. {instruction_text} If the reference content has no information reference, the topic can be generated in line with the task. \n\n Please generate more specific topics. Be creative and imaginative. Reply in 50 words or less. Don't add anything else.
        """
        
        ans = ask_llm(self.session, prompt)
        return ans


    def _get_title_name(self, main_idea: str, language: str = "English", instruction: Optional[str] = None) -> str:
        """
        Generates a title for an article based on a given main idea and potentially an additional user instruction.
        """
        
        # Include the instruction in the prompt if provided
        instruction_text = f" Consider this additional guidance: '{instruction}'." if instruction else ""
        
        prompt = f"""You are a "title generator" and you can generate titles based on specific central topics. No matter what the input language is, you must output text in {language}.
        There is a central theme "{main_idea}".{instruction_text} Please refine the corresponding title based on the central theme and the guidance provided, and ensure the response is no more than 15 words. Don't add anything else.
        """
        
        ans = ask_llm(self.session, prompt)
        return ans


    def _get_introduction(
        self,
        task_name: str,
        main_idea: str,
        character_a: str,
        language: str = "English",
        knowledge_content: Optional[str] = None,
        instruction: Optional[str] = None
    ) -> str:
        """
        Generate the content of the first paragraph of the article based on the given task name, main idea,
        character, knowledge content, language, and an optional user instruction.
        """
        # If there is an additional instruction, include it in the prompt
        instruction_text = f" Additionally, consider the following instruction: '{instruction}'." if instruction else ""
        
        prompt = f"""You're a {character_a}. Please create the content of the first paragraph of the article based on the reference content I give you and the task and central theme I assign to you. {instruction_text} If the reference content has no information reference, the theme can be generated in line with the task. \n\n Reference content: \n{knowledge_content}\n\n. No matter what the input language is, you must output text in {language}. \n Output requirements are as follows :\n
        1. Required to demonstrate expertise in the field.
        2. Require rich content and guide the full text.
        3. The word requirement is about 200 words.
        4. output the text in bulletpoints
        Please create the first paragraph based on the task {task_name} and the central topic {main_idea}.
        """
        ans = ask_llm(self.session, prompt)
        return ans


    def _get_muti_sub_idea(
        self,
        task_name: str,
        main_idea: str,
        character_a: str,
        introduction: str,
        language: str = "English",
        knowledge_content: Optional[str] = None,
        instruction: Optional[str] = None
    ) -> str:
        """
        Generate multiple sub-themes based on the task name, central theme, and the content of the first paragraph.
        """
        instruction_text = f" Consider this additional guidance for breaking down the themes: '{instruction}'." if instruction else ""
        
        prompt = f"""You're a {character_a}. Based on the reference content I gave you, please break down the central theme into multiple sub-themes according to the task name, central theme, and the content of the first paragraph. {instruction_text} Please arrange them in a logical order. \n\n Reference content: \n{knowledge_content}\n\n. No matter what the input language is, you must output text in {language}.
        The task name is "{task_name}", the central topic is "{main_idea}", and the first paragraph of the article is "{introduction}". Please break down the central topic into several sub-topics as the point of view of the essay. Brief content is required. Less than 15 words per subtopic. The format is \n1. \n2.
        """
        ans = ask_llm(self.session, prompt)
        return ans


    def _get_sub_content(
        self,
        task_name: str,
        main_idea: str,
        sub_idea: str,
        character_a: str,
        language: str = "English",
        knowledge_content: Optional[str] = None,
        instruction: Optional[str] = None
    ) -> str:
        """
        Generate a paragraph of specific content based on the given task, main idea, sub idea, and character.
        """
        instruction_text = f" Please incorporate the following user instruction into the content if relevant: '{instruction}'." if instruction else ""
        
        prompt = f"""
        You're a {character_a}. Please, according to the task I have assigned to you, the central theme, generate a whole paragraph of specific content based on this sub-theme as part of the whole article. {instruction_text} \n\n can refer to: \n{knowledge_content}\n\n. No matter what the input language is, you must output text in {language}.
        Based on the background information of task {task_name} and main topic {main_idea}, output the content of the subtopic {sub_idea} in the subtopic of {task_name}. The content of the subtopic must be 200 characters, and the content is output in bullet points. The meaning must be fully expressed.
        """
        ans = ask_llm(self.session, prompt)
        return ans

    def _get_end_sentence(
    self,
    task_name: str,
    main_idea: str,
    introduction: str,
    sub_idea: str,
    character_a: str,
    language: str = "English",
    instruction: Optional[str] = None
) -> str:
        """
        Generate the content of the last paragraph based on the task name, the central theme of the article,
        the introduction, sub-ideas, and optionally, specific user instructions.
        """
        # Include user instruction in the prompt if provided
        instruction_text = f" Additionally, consider the following specific instruction: '{instruction}'." if instruction else ""
        
        prompt = f"""You are a {character_a}. Please create the content of the last paragraph based on the task name, the central theme of the article, the content of the first paragraph, and the main content of the article based on the reference content I gave you, and it is required to echo the first paragraph. {instruction_text} No matter what the input language is, you must output text in {language}.
        Finish the article based on the task name of "{task_name}", the central theme of "{main_idea}", the article content of "{sub_idea}", and the first paragraph of "{introduction}". The generated ending must correspond with the first paragraph of the article and incorporate any relevant aspects of the provided instruction if applicable. The conclusion should be about 200 words, and the output is in bullet points.
        """
        ans = ask_llm(self.session, prompt)
        return ans

# ==============================================================================
# markdown updater (internal use)
# ==============================================================================
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
    
    def _revise_md(self, 
                   page:int, 
                   opinion:str, 
                   read_path:str, 
                   character_a: str = "you are a professional researcher"):
        """
        Revise the markdown content.
        """
        index_path = os.path.join(os.path.dirname(read_path), "index.txt")
        md_path = os.path.join(os.path.dirname(read_path), "parts/")

        # Preparation work
        task_name = "write a summary"

        # Get the main idea
        main_idea = self._get_main_idea(
            task_name, character_a, knowledge_content = self.main_idea_knowledge
        )

        task_name = "revise the content based on the feedback"
        sections = self._read_index(index_path)
        
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

    def _delete_md(self, page:int, read_path:str):
        """
        Delete the markdown content, and update the index file
        """
        index_path = os.path.join(os.path.dirname(read_path), "index.txt")
        md_path = os.path.join(os.path.dirname(read_path), "parts/")

        sections = self._read_index(index_path)
        section = sections[page - 1]
        section_type, filename = section

        chunk_path = os.path.join(os.path.dirname(md_path), filename)
        os.remove(chunk_path)
        sections.pop(page - 1)

        with open(index_path, 'w', encoding='utf-8') as index_file:
            for section in sections:
                section_type, filename = section
                index_file.write(section_type + "," + filename + '\n')

# ==============================================================================
# function for constructing markdown files (external use)
# ==============================================================================
    def _read_index(self, index_path):
        """
        Read the index file and return the sections
        """
        sections = []
        with open(index_path, 'r', encoding='utf-8') as index_file:
            for line in index_file:
                section_type, filename = line.strip().split(',')
                sections.append((section_type, filename))
        return sections

# ==============================================================================
# markdown generator/updater (external use)
# ==============================================================================
    def generate_md_artical(
        self,
        save_path,
        task_name: str = "write a summary",
        character_a: str = "you are a professional researcher",
        instruction: Optional[str] = None  
    ):
        """
        Generates the final summary for a given task. The summary are divided into parts and saved in the respective md files
        """
        md_dir = os.path.join(save_path, "parts/")
        index_dir = os.path.join(save_path, "index.txt")

        serial = 1
        filenames = []

        # Check Directiory Existence
        if not os.path.exists(md_dir):
            # If it doesn't exist, create it
            os.makedirs(md_dir)
            print(f"Directory '{md_dir}' created successfully.")

        # Get the article summary
        article_summary = self.main_idea_knowledge

        # Get the main idea
        main_idea = self._get_main_idea(
            task_name, character_a, knowledge_content=article_summary, instruction=instruction
        )

        # Get the title name
        title_name = self._get_title_name(main_idea, instruction=instruction)
        title_name =  "# " + title_name + "\n"
        save_md(title_name, md_dir + str(serial) +  "_title.md")
        filenames.append("title," + str(serial) +  "_title.md")
        serial += 1


        # Get the introduction
        introduction = self._get_introduction(
            task_name, main_idea, character_a, knowledge_content=article_summary, instruction=instruction
        )

        # Add the abstract section to the content
        save_md("\n## Introduction\n\n" + introduction, md_dir + str(serial) +  "_introduction.md")
        filenames.append("introduction," + str(serial) +  "_introduction.md")
        serial += 1

        # Get multiple sub-ideas until the minimum number is reached
        sub_ideas_list = []

        while True:
            sub_ideas = self._get_muti_sub_idea(
                task_name,
                main_idea,
                character_a,
                introduction,
                knowledge_content=article_summary,
                instruction=instruction
            )
            sub_ideas_list += get_sublist(sub_ideas)
            if len(sub_ideas_list) >= self.min_sub_idea_num:
                break

        # Renumber the sub-ideas
        sub_ideas_list_new = []

        for sub_idea in sub_ideas_list:
            sub_idea_new = ".".join(sub_idea.split(".")[1:])
            sub_idea_new = str(len(sub_ideas_list_new) + 1) + "." + sub_idea_new
            sub_ideas_list_new.append(sub_idea_new)

        # Limit the number of sub-ideas
        sub_ideas_list = sub_ideas_list_new[: self.max_sub_idea_num]


        # Generate content for each sub-idea
        for sub_idea_i in sub_ideas_list:

            sub_section = "\n\n## " + sub_idea_i

            #save_md(sub_idea_i, md_dir + str(serial) +  "_sub_idea_i.md")

            # Get the sub-knowledge if there's specified knowledge
            sub_knowledge_content = " "
            # Get the sub-content
            sub_content = self._get_sub_content(
                task_name,
                main_idea,
                sub_idea_i,
                character_a,
                knowledge_content=sub_knowledge_content,
                instruction=instruction
            )

            sub_section = sub_section + "\n\n" + sub_content

            save_md(sub_section, md_dir + str(serial) +  "_sub_section.md")
            filenames.append("subsection," + str(serial) +  "_sub_section.md")
            serial += 1

        # Get the end sentence
        end_sentence = self._get_end_sentence(
            task_name, main_idea, introduction, sub_ideas, character_a, instruction=instruction
        )

        save_md("\n\n## Conclusion\n\n" + end_sentence, md_dir + str(serial) +  "_end_sentence.md")
        filenames.append("conclusion," + str(serial) +  "_end_sentence.md")
        serial += 1

        with open(index_dir, 'w', encoding='utf-8') as index_file:
            for filename in filenames:
                index_file.write(filename + '\n')

    def combine_mds(self, read_path, task_name):
        index_path = os.path.join(read_path, 'index.txt')
        md_path = os.path.join(read_path, 'parts/')
        output_path = os.path.join(read_path, f'{task_name}.md')
        sections = self._read_index(index_path)

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
        
    def update_md(self, path, opinion):
        """
        Update the markdown content.
        first step ask llm to parse opinions into three categories : revise/delete/regenrate the content based on the feedback.
        then call the respective function to update the content.
        """


if __name__ == "__main__":
    character_a = "You're an experienced technologist"
    task_name = "Attention Mechanism"
    article_md = MarkdownGenerator()
    content = article_md.generate_md_artical(task_name, character_a)
    save_md(content, task_name + ".md")