from h2ogpte import H2OGPTE
from markdown_generator import MarkdownGenerator
from pdf_reader import ingest_documents
from utils import save_md

from config import API_KEY, PDF_PATH, PPT_DIR, REMOTE_ADDRESS

task_name = "attention"  # place holder

if __name__ == "__main__":

    client = H2OGPTE(address=REMOTE_ADDRESS, api_key=API_KEY)
    collection_id = None
    name = "h2ogpte Python client demo"

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
        save_md(content, f"{PPT_DIR}{task_name}.md")

    # Generate the ppt
    # ppt_gen = PptGenerator()
    # ppt_gen.generate_ppt(content, "./my_ppts/{}.pptx")
