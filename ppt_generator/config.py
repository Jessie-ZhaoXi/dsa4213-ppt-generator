"""
This module contains configuration settings for the DSA4213 PPT Generator.

API_KEY: str
    The API key used for authentication.

REMOTE_ADDRESS: str
    The remote address of the server used for communication.
"""

from pydantic_settings import BaseSettings

MD_DIR = "./my_mds/"
PDF_PATH = "./data/attention.pdf"
PPT_DIR = "./my_ppts/"
PPT_MODE_DIR = "./ppt_mode/"
LLM_ARGS = dict(temperature=0, do_sample=False, top_k=1, seed=4213)


class Settings(BaseSettings):
    H2OGPTE_API_TOKEN: str = ""
    H2OGPTE_URL: str = "https://h2ogpte.genai.h2o.ai"
    COLLECTION_NAME: str = "supersonic_rocket_ppt_generator"

    class Config:
        env_file = ".env"  # The file to read environment variables from


H2OGPTE_SETTINGS = Settings()
