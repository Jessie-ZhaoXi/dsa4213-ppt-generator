from typing import Optional

from h2ogpte import Session
from utils import get_sublist, save_md
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


class MarkdownGenerator:

    def __init__(
        self,
        session: Session,
        min_sub_idea_num: int = 2,
        max_sub_idea_num: int = 5,
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

    def _get_main_idea(
        self,
        task_name: str,
        character_a: str,
        language: str = "English",
        knowledge_content: Optional[str] = None,
    ) -> str:
        """
        Generates the main idea of the article based on the given task name, character, and reference content.
        """

        prompt = f"""You are a {character_a}. You can generate specific central themes based on a task. No matter what the input language is, you must output text in {language}.
        There is a task "{task_name}". Please generate the main idea of the article of this task type based on the reference content of the uploaded PDF I gave you. If the reference content has no information reference, the topic can be generated in line with the task. \n\n Please generate more specific topics. Be creative and imaginative. Reply in 50 words or less. Don't add anything else.
        """
        ans = ask_llm(self.session, prompt)
        return ans

    def _get_main_idea(
        self,
        task_name: str,
        character_a: str,
        language: str = "English",
        knowledge_content: Optional[str] = None,
    ) -> str:
        """
        Generate the main idea of the article based on the given task and reference content.
        """
        prompt = f"""You are a {character_a}，You can generate specific central themes based on a task. No matter what the input language is, you must output text in {language}.
        There is a task”{task_name}“,Please generate the main idea of the article of this task type based on the reference content of the uploaded pdf I gave you. If the reference content has no information reference, the topic can be generated in line with the task. \n\n Please generate more specific topics. Be creative and imaginative. Reply in 50 words or less. Don't add anything else.
        """
        ans = ask_llm(self.session, prompt)
        return ans

    def _get_title_name(self, main_idea: str, language: str = "English") -> str:
        prompt = f"""You are a "title generator" and you can disaggregate titles based on specific central topics. No matter what the input language is, you must output text in {language}.
        There is a central theme "{main_idea}", please refine the corresponding title based on the central theme, and ask the response to be no more than 15 words. Don't add anything else.
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
    ) -> str:
        """
        Generate the content of the first paragraph of the article based on the given task name, main idea,
        character, knowledge content, and language.
        """
        prompt = f"""You're a {character_a}. Please create the content of the first paragraph of the article based on the reference content I give you and the task and central theme I assign to you. If there is no information reference in the reference content, the theme can be generated in line with the task. \n\n Reference content: \n{knowledge_content}\n\n. No matter what the input language is, you must output text in {language}. \n Output requirements are as follows :\n
        1. Required to demonstrate expertise in the field.
        2. Require rich content and guide the full text.
        3. The word requirement is about 200 words
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
    ) -> str:
        """
        Generate multiple sub-themes based on the task name, central theme, and the content of the first paragraph.
        """
        prompt = f"""You're a {character_a}. Based on the reference content I gave you, please break down the central theme into multiple sub-themes according to the task name, central theme, and the content of the first paragraph. Please arrange them in a logical order. \n\n Reference content: \n{knowledge_content}\n\n. No matter what the input language is, you must output text in {language}.
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
    ) -> str:
        """
        Generate a paragraph of specific content based on the given task, main idea, sub idea, and character.
        """
        prompt = f"""
        You're a {character_a}. Please, according to the task I have assigned to you, the central theme, generate a whole paragraph of specific content based on this molecular theme as part of the whole article. \n\n can refer to: \n{knowledge_content}\n\n. No matter what the input language is, you must output text in {language}.
        Based on the background information of task {task_name} and main topic {main_idea}, output the content of the subtopic {sub_idea} in the subtopic of {task_name}. The content of the subtopic must be 200 characters. The meaning must be fully expressed.
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
    ) -> str:
        """
        Generate the content of the last paragraph based on the task name, the central theme of the article,
        """
        prompt = f"""：you are a {character_a}. Please create the content of the last paragraph based on the task name, the central theme of the article, the content of the first paragraph and the main content of the article based on the reference content I gave you, and it is required to echo the first paragraph. No matter what the input language is, you must output text in {language}.
        Finish the article based on the task name of "{task_name}", the central theme of "{main_idea}", the article content of "{sub_idea}", and the first paragraph of "{introduction}". The generated ending must correspond with the first paragraph of the article. 200 words required.
        """
        ans = ask_llm(self.session, prompt)
        return ans

    def generate_md_artical(
        self,
        task_name: str = "write a summary",
        character_a: str = "you are a professional researcher",
    ) -> str:
        """
        Generates the final summary for a given task.
        """
        # Get the article summary
        article_summary = self.main_idea_knowledge

        # Get the main idea
        main_idea = self._get_main_idea(
            task_name, character_a, knowledge_content=article_summary
        )

        # Get the title name
        title_name = self._get_title_name(main_idea)

        # Initialize the content
        all_content = "# " + title_name + "\n"

        # Print the central theme and title
        print("central theme:", main_idea)
        print("title:", title_name)
        print("======================")

        # Get the introduction
        introduction = self._get_introduction(
            task_name, main_idea, character_a, knowledge_content=article_summary
        )

        # Add the abstract section to the content
        all_content += "\n## Introduction\n\n" + introduction
        print("Introduction:", introduction)

        # Get multiple sub-ideas until the minimum number is reached
        sub_ideas_list = []

        while True:
            sub_ideas = self._get_muti_sub_idea(
                task_name,
                main_idea,
                character_a,
                introduction,
                knowledge_content=article_summary,
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

        # Print the total number of subtopics
        print("total number of subtopics:", len(sub_ideas_list))
        print("===============================")

        # Generate content for each sub-idea
        for sub_idea_i in sub_ideas_list:
            print(sub_idea_i)
            print(
                "------------------------------------------------------------------------------"
            )
            all_content += "\n\n## " + sub_idea_i

            # Get the sub-knowledge if there's specified knowledge
            sub_knowledge_content = " "
            # Get the sub-content
            sub_content = self._get_sub_content(
                task_name,
                main_idea,
                sub_idea_i,
                character_a,
                knowledge_content=sub_knowledge_content,
            )
            all_content += "\n\n" + sub_content
            print(sub_content)
            print("----------------------------")

        # Get the end sentence
        end_sentence = self._get_end_sentence(
            task_name, main_idea, introduction, sub_ideas, character_a
        )
        print("===============================")

        # Add the summary section to the content
        all_content += "\n\n## Conclusion\n\n" + end_sentence

        # Print the end sentence
        print("the end:", end_sentence)

        return all_content


if __name__ == "__main__":
    character_a = "You're an experienced technologist"
    task_name = "Attention Mechanism"
    article_md = MarkdownGenerator()
    content = article_md.generate_md_artical(task_name, character_a)
    save_md(content, task_name + ".md")