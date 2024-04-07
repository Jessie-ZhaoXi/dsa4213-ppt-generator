import os
import pathlib

from h2ogpte import H2OGPTE


def ingest_documents(
    client: H2OGPTE,
    collection_name: str,
    collection_id: str,
    pdf_path: str,
    is_local: bool = True,
):
    """
    Ingests documents into the H2OGPTE client.
    """
    # Upload file into collection
    file_path = (
        pathlib.Path(os.path.basename(pdf_path))
        if not is_local
        else pathlib.Path(pdf_path)
    )
    with open(file_path.resolve(), "rb") as f:
        print(
            f"Uploading {file_path} to collection {collection_name} ({collection_id})"
        )
        upload_id = client.upload(file_path.name, f)

    print("Converting the input into chunked text and embeddings...")
    client.ingest_uploads(collection_id, [upload_id])
    print(f"DONE: {collection_id}")
    return collection_id