# dsa4213-ppt-generator

### Quick Start
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

To run the wave app, check that your present working directory is at /frontend_explore
```
wave run src/app.py
```
### For developers
before commit the python code, the developer can use `make format` command for the auto code formatting.
