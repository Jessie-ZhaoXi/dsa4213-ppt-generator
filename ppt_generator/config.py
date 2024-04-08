"""
This module contains configuration settings for the DSA4213 PPT Generator.

API_KEY: str
    The API key used for authentication.

REMOTE_ADDRESS: str
    The remote address of the server used for communication.
"""

from pydantic_settings import BaseSettings

API_KEY = ""
REMOTE_ADDRESS = "https://h2ogpte.genai.h2o.ai"
PDF_PATH = "./data/attention.pdf"
PPT_DIR = "./my_ppts/"
PPT_MODE_DIR = "./ppt_mode/"
LLM_ARGS = dict(
              temperature=0,
              do_sample = False,
              top_k = 1,
              seed = 4213)


# class Settings(BaseSettings):
#     APP_NAME: str = "AppName"
#     SQLALCHEMY_URL: str
#     ENVIRONMENT: str

#     class Config:
#         env_file = ".env"  # Works with uvicorn run command from my-app/project/
#         # env_file = "../.env"  Works with alembic command from my-app/alembic
#         # env_file = abs_path_env


# def get_settings():
#     return Settings()
