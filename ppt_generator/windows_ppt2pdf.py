from spire.presentation.common import *
from spire.presentation import *

def win_ppt2pdf(inputFile:str = "attention_mode2.pptx", outputFile:str = "ToPDF.pdf"):
    #Create a PPT document
    presentation = Presentation()

    #Load PPT file from disk
    presentation.LoadFromFile(inputFile)

    #Save the PPT to PDF file format
    presentation.SaveToFile(outputFile, FileFormat.PDF)
    presentation.Dispose()