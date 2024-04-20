prompts_eng = {
    'system_prompt': """You are a virtual assistant called SlidesGPT.
Please answer in English.
Answer the question with information provided in the context, do not create any information.
If you do not have enough information to answer your question, inform in english about the information that is missing to provide a complete answer.""",
    "pre_prompt_summary":"Using only the document chunks below, make a summary that best describes the subject of the ingested document and the author's requests. Do not add any facts not described in the text.\n",
    "prompt_summary": "Describe the subject and the facts in a summary in English.",
    "ppt_prompt": """Answer only using the chunks above from the ingested document.\n\nQUESTION:{0} \n\nANSWER:"""
}


sum_check = ['gimme a summary', 'give me a summary', 'summarize this', 'summarize this pdf', 'summarize this file',
            'summarize the paragraph']

