# dsa4213-ppt-generator

## Quick Start
Install the required python dependencies
```
pip install -r requirements.txt
```
Or install dependencies with `poetry`
```bash
# project using Python version 3.10.6 currently
# export dependencies to a requirements.txt file without hashes to decrease time to resolve dependencies
# poetry export --without-hashes --format=requirements.txt > requirements.txt
poetry install
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
```

### Run the Wave APP
To run the wave app, check that your present working directory is at /frontend_explore
```
wave run src/app.py
```
In the interface, the user is asked to upload a pdf file. The ppt generator will then generate a ppt based on the uploaded pdf.

The loading process will take a longer time since it needs to generate detailed content of each slides.

### Run the Colab for the whole pipeline
We have prepared a working colab notebook for the user to try our our product! We recommond the user to use this colab to run our code, as our code uses the Spire.PDF package which cannot be installed in macos system. The colab link is https://colab.research.google.com/drive/1X-v6yxTXmPE99xK1crFyd0Ae-AYAZwD2#scrollTo=VQJgbnnBden1 .

The user just need to run cell by cell following the instruction. The are three thing user has to modify to input the API Tokens:
1. First of all, user has to upload the pdf file manually to the 'uploaded' folder under 'dsa4213-ppt-generator/'.
2. Secondly, user has the modify the API TOKEN in the 'dsa4213-ppt-generator/ppt_generator/config.py' file.
3. Lastly, user has to to apply a ngrok token via https://dashboard.ngrok.com/tunnels/authtokens/new and paste the token here ![image](https://github.com/Jessie-ZhaoXi/dsa4213-ppt-generator/assets/89125308/a9dd963b-0bae-489c-89cd-3997d8da5bf8).

Additionally, remember to key in yes in the red box when running the first cell ![image](https://github.com/Jessie-ZhaoXi/dsa4213-ppt-generator/assets/89125308/77ce2284-a629-4d49-85be-e75513ad09b9).

We have to manually install the wave binary and run it as the h2o_wave python package cannot initialise the wave server. 




### For developers
before commit the python code, the developer can use `make format` command for the auto code formatting.
