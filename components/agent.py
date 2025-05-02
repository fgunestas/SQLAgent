from typing import Annotated, Sequence, TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import  BaseMessage
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2:3b", base_url="http://localhost:11434")

# SQL bağlantısı
from sqlalchemy import create_engine, text
engine = create_engine("sqlite:///chinook.db")


class State(TypedDict):
    prompt: str
    query: str


def query_generator(state):
    prompt = state["prompt"]
    prompt = f"Aşağıdaki soruya uygun bir SQL sorgusu yaz sadece SQL olarak döndür:\nSoru: {prompt}"
    response = llm.invoke(prompt).content
    return {"messages": [response]}


def query_executor(state):
    query = state["messages"]
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query)).fetchall()
        return {"query_result": result}
    except Exception as e:
        return {"query_result": f"SQL Error: {str(e)}"}



def response_generator(state):
    messages = state["messages"]
    result = state["query_result"]
    prompt = f"Soru: {messages}\nVeritabanı çıktısı: {result}\nBu çıktıyı kullanıcıya açıklayıcı şekilde özetle."
    response = llm.invoke(prompt).content

    return {"messages": [response]}