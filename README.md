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
### For developers
before commit the python code, the developer can use `make format` command for the auto code formatting.
