from spire.pdf import *
import re
from h2ogpte import H2OGPTE
from ppt_generator.utils import *
from ppt_generator.config import *
import logging
from argparse import ArgumentParser
import os


class PDF_Reader:
  def __init__(self):
    self.doc = PdfDocument()
    pass

  def load_pdf(self, path):
    logging.info(path)
    self.doc.LoadFromFile(path)

  def extract_text_and_image(self, image_output_folder, client):
    if self.doc.Pages.Count == 0:
      print('Please Check Whether You Have Loaded a PDF Correctly.')
      return

    pattern = r'Figure (\d+):(.*?\.)\n'
    dic = {}
    logging.info("Start to extract text and images")
    for i in range(self.doc.Pages.Count):
      page = self.doc.Pages.get_Item(i)
      text = page.ExtractText()

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
      
    
    self.dic = dic
  
  def parse_description(self, description, num_images, client):
    if num_images > 1:
      ## Use LLM to handle. TODO
      llm = "h2oai/h2ogpt-4096-llama2-13b-chat"
      logging.info("Start to parse image descriptions")
      question = '''
      Suppose now I am extracting the title or description of some images in PDF, the text may include more than one image titles. Can you help me split it? Please just return the result.
      Description: {}'''

      answer = client.answer_question(llm_args = LLM_ARGS,question= question.format(description), llm=llm).content
      
      pattern = r'\d+\.\s*(.*?)(?:\n|$)'

      # Find all matches in the text
      return extract_text_using_regex(answer, pattern)
    else:
      return [description]

if __name__ == '__main__':
  parser = ArgumentParser(description = 'Horn Schunck program')
  parser.add_argument('pdf_path', type = str, help = 'Path of the pdf file')
  args = parser.parse_args()

  if not os.path.exists('data'):
    os.mkdir('data' + "/")

   
  h2ogpte_keys = {
                "address": H2OGPTE_SETTINGS.H2OGPTE_URL,
                "api_key": H2OGPTE_SETTINGS.H2OGPTE_API_TOKEN,
            }
  client = H2OGPTE(h2ogpte_keys['address'], h2ogpte_keys['api_key'])
  pdf_reader = PDF_Reader()
  pdf_reader.load_pdf(args.pdf_path)
  image_output_folder = 'data'
  pdf_reader.extract_text_and_image(image_output_folder, client)
  json_path = IMG_DESCRIPTION_DIC_PATH
  dump_json(pdf_reader.dic, json_path)
  