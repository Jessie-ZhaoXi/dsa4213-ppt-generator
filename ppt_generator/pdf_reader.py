import os
import pathlib
#from spire.pdf import *
import re
from h2ogpte import H2OGPTE
from utils import *
from config import *


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
    #pdf_reader = PDF_Reader()
    #pdf_reader.load_pdf(pdf_path)
    #text_path, image_output_folder = 'data/attention.txt', 'data'
    #pdf_reader.extract_text_and_image(text_path, image_output_folder, client)
    json_path = IMG_DESCRIPTION_DIC_PATH
    #dump_json(pdf_reader.dic, json_path)


    text_path = 'data/attention.txt'


    file_path = (
        pathlib.Path(os.path.basename(text_path))
        if not is_local
        else pathlib.Path(text_path)
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

class PDF_Reader:
  def __init__(self):
    #self.doc = PdfDocument()
    pass

  def load_pdf(self, path):
    self.doc.LoadFromFile(path)

  def extract_text_and_image(self, text_output_path, image_output_folder, client):
    extractedText = open(text_output_path, "w", encoding="utf-8")
    if self.doc.Pages.Count == 0:
      print('Please Check Whether You Have Loaded a PDF Correctly.')
      return

    pattern = r'Figure (\d+):(.*?\.)\n'
    dic = {}
    for i in range(self.doc.Pages.Count):
      page = self.doc.Pages.get_Item(i)
      text = page.ExtractText()
      extractedText.write(text + "\n")

      images = page.ExtractImages()
      if images:
        matches = re.search(pattern, text,re.DOTALL)
        figure_number = matches.group(1)
        figure_description = matches.group(2).replace("\n", "").replace("\r", "")
      
        descriptions = self.parse_description(figure_description, len(images), client)
        if len(images) != len(descriptions):
          images = images[:len(descriptions)]
        for i in range(len(images)):
          image, description = images[i], descriptions[i]
          image_file_name = "{}/Figure_{}_{}.png".format(image_output_folder, figure_number, i)
          image.Save(image_file_name,ImageFormat.get_Png())
          dic[image_file_name] = description
      
    extractedText.close()
    self.dic = dic
  
  def parse_description(self, description, num_images, client):
    if num_images > 1:
      ## Use LLM to handle. TODO
      llm = "h2oai/h2ogpt-4096-llama2-13b-chat"

      question = '''
      Suppose now I am extracting the title or description of some images in PDF, the text may include more than one image titles. Can you help me split it? Please just return the result.
      Description: {}'''

      answer = client.answer_question(llm_args = LLM_ARGS,question= question.format(description), llm=llm).content
      
      pattern = r'\d+\.\s*(.*?)(?:\n|$)'

      # Find all matches in the text
      return extract_text_using_regex(answer, pattern)
    else:
      return [description]