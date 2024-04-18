from ppt_generator.config import *
from typing import Tuple
from h2ogpte import H2OGPTE
from ppt_generator.markdown_generator import MarkdownGenerator
from ppt_generator.pdf_reader import ingest_documents
from ppt_generator.utils import *
from ppt_generator.md2ppt import PptGenerator
from typing import Optional

"""
This script demonstrates how to use the h2ogpte Python client to generate a PowerPoint presentation from a PDF file.
"""

task_name = "attention"  # place holder
name = "h2ogpte Python client demo resnet text" # Name should be modified according to the file_name

def create_client_and_collection()-> Tuple[H2OGPTE, str]:
    # Connect to the server
    client = H2OGPTE(address=H2OGPTE_SETTINGS.H2OGPTE_URL, api_key=H2OGPTE_SETTINGS.H2OGPTE_API_TOKEN)
    collection_id = None
    print("Recent collections:")
    recent_collections = client.list_recent_collections(0, 1000)
    for c in recent_collections:
        if c.name == name and c.document_count:
            collection_id = c.id
            break
    # Create Collection
    if collection_id is None:
        print(f"Creating collection: {name} ...")
        collection_id = client.create_collection(
            name=name,
            description="PDF -> text -> summary",
        )
        print(f"New collection: {collection_id} ...")
    return client, collection_id

def oneshot_generate_ppt(client: H2OGPTE, session:Session, task_name: str, min_sub_idea_num: int = 2,
                         max_sub_idea_num: int = 6, instruction: Optional[str] = None) -> MarkdownGenerator:
    """
    This function will be integrated with the frontend to generate a markdown file and a PowerPoint presentation from a PDF file.
    Generate a markdown file and a PowerPoint presentation from a PDF file.
    """
    # Generate the markdown file
    print("Generating markdown file ...")
    article_md = MarkdownGenerator(session, min_sub_idea_num = min_sub_idea_num, max_sub_idea_num = max_sub_idea_num)
    print("create markdown generator")
    article_md.generate_md_artical(
        save_path=MD_DIR, instruction=instruction
    )
    md_content = article_md.combine_mds(MD_DIR, task_name)
    image_mapping_dic = generate_ppt_image_mapping(IMG_DESCRIPTION_DIC_PATH, md_content, client)
    # Generate the ppt
    for i in range(1, 3):  # generate two modes of ppt
        PptGenerator(
            client,
            image_mapping_dic,
            md_content,
            PPT_MODE_DIR + str(i),
            save_path=PPT_DIR + task_name + "_mode" + str(i) + ".pptx",
        )
    return article_md

def main():
    # Create client and collection
    client, collection_id = create_client_and_collection()
    chat_session_id = client.create_chat_session(collection_id)
    collection_id = ingest_documents(client, name, collection_id, PDF_PATH)
    chat_session_id = client.create_chat_session(collection_id)
    print(f"Chat session ID: {chat_session_id}")
    with client.connect(chat_session_id) as session:
        image_list = read_image_description()
        min_sub_idea_num = len(image_list) + 1
        max_sub_idea_num = min_sub_idea_num + 2
        instruction = f"please generate at least {min_sub_idea_num} number of sub-ideas to include idea in {image_list}, with each one as a individual sub-idea" if image_list else ""
        article_md=oneshot_generate_ppt(client, session, task_name, min_sub_idea_num, max_sub_idea_num, instruction=instruction)
        # update the marlkdown file
        """ 
        output_mag = article_md.update_md(path = MD_DIR, opinion= "haha just joking i'm testing")
        print(f"Updated markdown file: {output_mag}")
        md_content = article_md.combine_mds(MD_DIR, task_name)
        image_mapping_dic = generate_ppt_image_mapping(IMG_DESCRIPTION_DIC_PATH, md_content, client)
        for i in range(2, 3):  # generate two modes of ppt
            PptGenerator(
                client,
                image_mapping_dic,
                md_content,
                PPT_MODE_DIR + str(i),
                save_path=PPT_DIR + task_name + "_mode" + str(i) + ".pptx",
            )
        """


if __name__ == "__main__":
    main()