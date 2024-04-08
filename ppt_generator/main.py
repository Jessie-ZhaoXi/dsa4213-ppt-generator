from h2ogpte import H2OGPTE
from ppt_generator import PptGenerator
from utils import *

from config import *
from markdown_generator import MarkdownGenerator
from pdf_reader import ingest_documents
from markdown_parser import parse_str

"""
This script demonstrates how to use the h2ogpte Python client to generate a PowerPoint presentation from a PDF file.
"""

task_name = "attention"  # place holder


def main():
    # Connect to the server
    client = H2OGPTE(address=REMOTE_ADDRESS, api_key=API_KEY)
    collection_id = None
    ## Name should be modified according to the file_name
    name = "h2ogpte Python client demo resnet text"

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

    # Read the pdf
    collection_id = ingest_documents(client, name, collection_id, PDF_PATH)

    # Generate markdown
    chat_session_id = client.create_chat_session(collection_id)
    with client.connect(chat_session_id) as session:
        # Generate the summary
        article_md = MarkdownGenerator(session)
        content = article_md.generate_md_artical()
        if not os.path.exists(PPT_DIR):
            # If it doesn't exist, create it
            os.makedirs(PPT_DIR)
            print(f"Directory '{PPT_DIR}' created successfully.")
        save_md(content, f"{PPT_DIR}{task_name}.md")

    # Generate the ppt
    md_content = read_md_file(PPT_DIR + task_name + ".md")
    out = parse_str(md_content)

    for i in range(1, 3):  # generate two modes of ppt
        PptGenerator(
            md_content,
            PPT_MODE_DIR + str(i),
            save_path=PPT_DIR + task_name + "_mode" + str(i) + ".pptx",
        )


if __name__ == "__main__":
    main()
