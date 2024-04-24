# dsa4213-ppt-generator

*This is the Github repository for the NUS DSA4213 team SuperSonic Rocket 🚀* 

A Powerpoint presentation generation tool: Transforms academic papers into PPT presentations with just a few clicks. Upload your PDF, and the LLM app will utilize the RAG pipeline to automatically analyze the content, extracting key texts and diagrams for seamless integration into dynamic and customizable slides.

Powered by H2O.ai, the tool features an intuitive interface for real-time adjustments and diverse styling options. Ideal for students and researchers, it simplifies the presentation of complex data-driven content. Elevate your academic presentations with precision and ease.

### Requirements

This project is build with python 3.10.6.
- Your API keys in your [h2ogpte account settings](https://h2ogpte.genai.h2o.ai)


### Run the Colab for the whole pipeline
We have prepared a [working colab notebook](https://colab.research.google.com/drive/1X-v6yxTXmPE99xK1crFyd0Ae-AYAZwD2#scrollTo=VQJgbnnBden1) for the user to try our our product! We recommond the user to use this colab to run our code, as our code uses the Spire. PDF package which cannot be installed in macos system. 

The user just need to run cell by cell following the instruction. The are three thing user has to modify to input the API Tokens:
1. First of all, user has to upload the pdf file manually to the 'uploaded_files' folder under 'dsa4213-ppt-generator/'.
2. Secondly, user has the modify the API TOKEN in the 'dsa4213-ppt-generator/ppt_generator/config.py' file.
3. Lastly, user has to to apply a ngrok token via https://dashboard.ngrok.com/tunnels/authtokens/new and paste the token here ![image](https://github.com/Jessie-ZhaoXi/dsa4213-ppt-generator/assets/89125308/a9dd963b-0bae-489c-89cd-3997d8da5bf8)

Additionally, remember to key in yes in the red box when running the first cell ![image](https://github.com/Jessie-ZhaoXi/dsa4213-ppt-generator/assets/89125308/77ce2284-a629-4d49-85be-e75513ad09b9)

Also, we have to click the first link here in order to access the app ![image](https://github.com/Jessie-ZhaoXi/dsa4213-ppt-generator/assets/89125308/451cdee2-dec6-43cf-88f9-4b49de4ba7b7)


We have to manually install the wave binary and run it as the h2o_wave python package cannot initialise the wave server. 

## Quick start in your local machine

Clone this GitHub repo and cd to its directory

```bash
git clone https://github.com/Jessie-ZhaoXi/dsa4213-ppt-generator.git
cd dsa4213-ppt-generator
```

Create venv and pip install the required python dependencies

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
Or use `poetry` install dependencies and create venv
```bash
poetry install
# run below command if your OS is Linux or Windows
# poetry add spire
```

### Getting the API keys
If you do not have an existing API key:
    Go to https://h2ogpte.genai.h2o.ai/settings, > APIs Tab, click 'New API key'

Save the API key and address to your environmental variables
```bash
touch .env
```
and then save and edit your enviroment variables inside the `.env` file
```
H2OGPTE_API_TOKEN='YOUR_KEY'
H2OGPTE_URL=https://h2ogpte.genai.h2o.ai
# COLLECTION_NAME="supersonic_rocket_ppt_generator"
# LLM="gpt-4-1106-preview"
```
### Preprocess to extract the images from PDF [Not applicable for Mac users]
We are use Spire.PDF to extract the images, and currently this package has some conflicts when running with the frontend's framework (THIS PACKAGE CANNOT BE INSTALLED IN macOS). Therefore our current approach is to run this step before we run our wave app. Please upload the pdf file under 'uploaded_files' folder and run the following code. Suppose you uploaded 'attention.pdf' in this folder then the code will be
```
cd dsa4213-ppt-generator/ && python ppt_generator/pdf_reader.py uploaded_files/attention.pdf data
```

### Run the Wave APP entrypoint
To run the wave app, check that your present working directory is at /dsa4213-ppt-generator
```
wave run src/app.py
```
In the interface, the user is asked to upload a pdf file. The ppt generator will then generate a ppt based on the uploaded pdf.

The loading process will take a longer time since it needs to generate detailed content of each slides.



### For developers
before commit the python code, the developer can use `make format` command for the auto code formatting.
