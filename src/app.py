import sys
sys.path.append('..')
from h2o_wave import Q, app, main, on, site, ui, run_on, copy_expando
import os
import logging
from pathlib import Path
import requests
from src.texts_app import texts_app_en
from ppt_generator.config import H2OGPTE_SETTINGS
from src.doc_qna_h2ogpte import QnAManager, H2OGPTEClient
from src.utils import loading
from src.constants import *
from src.layout import get_header_card, layout, get_home_items


logging.basicConfig(level=logging.INFO)

collection_name=H2OGPTE_SETTINGS.COLLECTION_NAME
collection_description="created for DSA4213 project"

llm = "mistralai/Mixtral-8x7B-Instruct-v0.1"

@app("/")
async def serve(q: Q):
    if not q.app.initialized:
        await initialize_app(q)
        q.app.initialized = True
    if not q.client.initialized:
        logging.info("New client session started.")
        q.client.texts = texts_app_en
        q.client.language = 'en' # or 'ptbr'
        await layout(q)
        await get_home_items(q, flag="home")
        await q.page.save()
        q.client.initialized = True
        
    q.client.qnamanager = QnAManager(q.app.h2ogpte, llm, q.client.collection_request_id, q.app.collection_id, q.client.language)    
    copy_expando(q.args, q.client)
    logging.debug('q.args: %s', q.args)
    await run_on(q)


async def initialize_app(q: Q): 
    q.app.h2ogpte_keys = {
                "address": H2OGPTE_SETTINGS.H2OGPTE_URL,
                "api_key": H2OGPTE_SETTINGS.H2OGPTE_API_TOKEN,
            }
    q.app.h2ogpte = H2OGPTEClient(q.app.h2ogpte_keys['address'], q.app.h2ogpte_keys['api_key'])
    q.app.collection_id = q.app.h2ogpte.create_collection(collection_name, collection_description)
    q.client.collection_request_id = q.app.h2ogpte.create_collection(collection_name, collection_description)
    q.app.loader, = await q.site.upload([LOADING_GIF])
    q.app.logo, = await q.site.upload([COMPANY_LOGO])
    q.app.backgroud, = await q.site.upload([BACKGROUND_IMAGE])


@on()
async def chatbot(q: Q):
    await on_generating(q, q.client.chatbot)


@on()
async def questions(q: Q):
    '''
    triggers on_generating function, which initiates a H20GPTE client instance.
    returns the Response.
    '''
    data = q.client.texts['questions_data']
    question_prompt = data['Question'][int(q.client.questions[0])]
    #await on_generating(q, question_prompt)
    print(f'question_prompt: {question_prompt}')
    await generate_ppt(q, question_prompt)


async def on_generating(q: Q, question_prompt: str):
    q.page["card_1"].data += [question_prompt, True]
    await q.page.save()
    output = await q.run(q.client.qnamanager.answer_question, q, question_prompt, q.client.path)


@on(arg='english')
async def set_english(q: Q):
    q.client.texts = texts_app_en
    q.client.language = 'en'
    await get_home_items(q, flag="home")
    await q.page.save()


@on()
async def file_upload(q: Q):
    try:
        paths = q.client['file_upload']
        print(f'Received file upload paths are {paths}.')
        if paths:
            for path in paths:
                local_path = await q.site.download(path, './uploaded_files')
                print(f'******######downloaded:{local_path}')
                q.client.path = local_path
                # ingest the file to the collection and save the MarkdownGenerator object in q.app.h2ogpte.article_md
                await q.run(q.app.h2ogpte.ingest_filepath, q.client.path, q.client.collection_request_id)
                print("q.app.h2ogpte.article_md", q.app.h2ogpte.article_md)
                await get_home_items(q, flag="uploaded")
        await q.page.save()
    except:
          q.page['meta'].dialog = None
          await get_home_items(q, flag="home")
          await q.page.save()

    # try:
    #     filename = q.client['file_upload']
    #     print(f'******{filename}')
    #     q.client.path = Path('./uploaded_files/' + filename)
    #     await loading(q)
    #     q.app.h2ogpte = H2OGPTEClient(q.app.h2ogpte_keys['address'], q.app.h2ogpte_keys['api_key'])
    #     q.client.collection_request_id = q.app.h2ogpte.create_collection(f'collection_{filename}', f'Collection for {filename}')
    #     q.client.qnamanager = QnAManager(q.app.h2ogpte, llm, q.client.collection_request_id, q.app.collection_id, q.client.language)
    #     await q.run(q.app.h2ogpte.ingest_filepath, q.client.path, q.client.collection_request_id)
    #     q.page['meta'].dialog = None
    #     await get_home_items(q, flag="uploaded")
    #     await q.page.save()
    # except:
    #     q.page['meta'].dialog = None
    #     await get_home_items(q, flag="home")
    #     await q.page.save()

async def generate_ppt(q: Q, instruction: str):
    try:
        print("Generating PPT...")
        await q.run(q.app.h2ogpte.generate_ppt, instruction)
    except Exception as e:
        print(f"Error during PPT generation: {e}")  # Log the exception to the console
        q.page['meta'].dialog = None
        await get_home_items(q, flag="home")
        await q.page.save()



@on()
async def reset(q: Q):
    await get_home_items(q, flag="home")
    await q.page.save()


def delete_filepath(filepath: str):
    import os
    try:
        os.unlink(filepath)
    except Exception as e:
        logging.warning('Failed to delete %s. Reason: %s' % (filepath, e))
