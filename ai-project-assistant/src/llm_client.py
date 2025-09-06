# src/llm_client.py
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

load_dotenv()

def get_openai_llm(model_name: str = "gpt-4", temperature: float = 0.2):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY in environment (or .env).")
    return ChatOpenAI(model=model_name, temperature=temperature, openai_api_key=key)

class LLMManager:
    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name
        self.llm = get_openai_llm(model_name)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.chain = ConversationChain(llm=self.llm, memory=self.memory)

    def ask(self, prompt: str) -> str:
        # simple wrapper: conversation chain predicts
        return self.chain.predict(input=prompt)

    def complete(self, prompt: str) -> str:
        # For one-shot summarization use the llm directly
        return self.llm.predict(prompt)
