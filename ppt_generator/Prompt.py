 class Prompt:
    def __init__(self, session: Session, llm: str = "gpt-4-1106-preview"):
        self.session = session
        self.llm = llm

    def get_response(self, question: str):
        response = self.session.query(
            message=question,
            llm=self.llm,
            rag_config={"rag_type": "rag"},
        ).content
        return response
