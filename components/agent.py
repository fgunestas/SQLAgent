from typing import Annotated, Sequence, TypedDict

from langchain_community.tools import QuerySQLDataBaseTool
from langgraph.graph.message import add_messages
from langchain_core.messages import  BaseMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

llm = ChatOllama(model="llama3.2:3b", base_url="http://localhost:11434")

# SQL bağlantısı

from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///chinook.db")


class State(TypedDict):
    messages: str
    query: str
    result: str
    response: str


from typing import Annotated

class QueryOutput(TypedDict):
    query: Annotated[str, ..., "Syntactically correct and valid SQL query"]




def query_generator(state):
    prompt = PromptTemplate.from_template("""Given an input question, create a syntactically correct {dialect} query to run to help find the answer."
              "Unless the user specifies in his question a specific number of examples they wish to obtain, always limit your query to at most {top_k} results."
              "You can order the results by a relevant column to return the most interesting examples in the database."
              "Never query for all the columns from a specific table, only ask for a the few relevant columns given the question."
              "Pay attention to use only the column names that you can see in the schema description."
              "Be careful to not query for columns that do not exist."
              "Also, pay attention to which column is in which table.)Only use the following tables:{table_info}"
              "Question: {input}""")

    prompt=prompt.format(table_info=db.get_table_info(),top_k=5,dialect=db.dialect,input = state["messages"])


    structured_llm = llm.with_structured_output(QueryOutput)

    result = structured_llm.invoke(prompt)

    return {"query": result["query"]}

def query_executor(state):
    query = state["query"]
    executor=QuerySQLDataBaseTool(db=db)

    return {'result': executor.invoke({"query": query})}



def response_generator(state):

    state["query"]='SELECT COUNT(*) FROM Employee'
    state["messages"]="How many employees are there?"

    #print(state["result"],
    #      state["query"],
    #      state["messages"])
    prompt = PromptTemplate.from_template("""
    Given the following user question, corresponding SQL query,
        and SQL result, answer the user question.
        Question: {messages}
        SQL Query: {query}
        SQL Result: {result}""")

    response=prompt.format(result=state["result"],query=state["query"],messages=state["messages"])
    response = llm.invoke(response)

    return {"response": response.content}