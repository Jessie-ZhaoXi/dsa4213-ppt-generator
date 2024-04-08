from spire.pdf import *
import re

class PDF_Reader:
  def __init__(self):
    self.doc = PdfDocument()

  def load_pdf(self, path):
    self.doc.LoadFromFile(path)

  def extract_text_and_image(self, text_output_path, image_output_folder):
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
      
        descriptions = self.parse_description(figure_description, len(images))
        if len(images) != len(descriptions):
          images = images[:len(descriptions)]
        for i in range(len(images)):
          image, description = images[i], descriptions[i]
          image_file_name = "{}/Figure_{}_{}.png".format(image_output_folder, figure_number, i)
          image.Save(image_file_name,ImageFormat.get_Png())
          dic[image_file_name] = description
      
    extractedText.close()
    self.dic = dic
  
  def parse_description(self, description, num_images):
    if num_images > 1:
      ## Use LLM to handle. TODO
      return ['Scaled Dot-Product Attention.', 'Multi-Head Attention consists of several                            attention layers running in parallel.']
    else:
      return [description]