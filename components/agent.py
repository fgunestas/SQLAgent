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
    prompt = PromptTemplate.from_template("""You are a helpful assistant that converts natural language questions into syntactically correct and relevant {dialect} SQL queries.

Given the user's question and the database schema, generate a query that can answer the question effectively.

Guidelines:
- Only use the table and column names provided in the schema below.
- Never query for all columns (e.g., SELECT *); instead, select only the most relevant columns for the question.
- If the question does not specify a number of results, limit the query to the top {top_k} results.
- If appropriate, order the results by a meaningful column to return the most informative data.
- Do not reference columns or tables that are not included in the schema.
- Ensure that the syntax is valid for the {dialect} dialect.
- Only use the following tables and schema:  
  {table_info}

User Question:
{input}

Generate only the SQL query. Do not include any explanation.""")

    prompt=prompt.format(table_info=db.get_table_info(),top_k=5,dialect=db.dialect,input = state["messages"])


    structured_llm = llm.with_structured_output(QueryOutput)

    result = structured_llm.invoke(prompt)

    return {"query": result["query"]}

def query_executor(state):
    query = state["query"]
    executor=QuerySQLDataBaseTool(db=db)

    return {'result': executor.invoke({"query": query})}



def response_generator(state):


    prompt = PromptTemplate.from_template("""
    You are an intelligent assistant tasked with interpreting the result of a SQL query.

Based on the user's original question, the SQL query that was generated, 
and the result returned from the database, provide a clear and helpful answer.

- User Question: {messages}
- Generated SQL Query: {query}
- SQL Result Table: {result}

Please respond with a concise and user-friendly explanation that directly addresses the user's question.""")

    response=prompt.format(result=state["result"],query=state["query"],messages=state["messages"])
    response = llm.invoke(response)

    return {"response": response.content}