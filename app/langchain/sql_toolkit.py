import os
import json
from langchain_community.utilities import SQLDatabase
from app.core import settings
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Optional, Annotated, List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from app.services import security
from langchain_core.runnables import RunnableLambda
from sqlalchemy import text
from datetime import date


os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
db = SQLDatabase.from_uri(settings.DATABASE_URL)
llm = init_chat_model(model="gemini-2.0-flash", model_provider="google_genai")

system = """
You are an agent designed to be a financial assistant to a user.
please, only write query for that user, based on the user's Id that is been passed
Never query the whole database, only what that user expects
Given an input question , create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

Use this available tables
Then you should query the schema of the most relevant tables.
{table}

Note: If user asks about their account balance, or balances, or how much they have in their accounts, or the sum total of all balances, in the accounts
just return all the balances or balance and not the sum total

Most importantly You are writing SQL for a PostgreSQL database. Use PostgreSQL date/time functions, not SQLite functions
Also, In PostgreSQL, always use single quotes for string values in SQL queries."
Lastly and MOST IMPORTANTLY, institution column of linked_accounts is of type JSON. When grouping or selecting distinct institutions, use institution->>'name' for the name, or institution::text to group by the whole object.
"""

template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            system,
        ),
        (
            "human",
            "{input}",
        ),
    ]
)


class State(TypedDict):
    id: str
    question: str
    query: str
    result: List
    answer: str


class QueryOutput(TypedDict):
    query: Annotated[
        str,
        ...,
        "Syntactically valid SQL query with returning both the field names together with their values",
    ]


class QuerySQLDatabaseToolWithFields(QuerySQLDataBaseTool):
    def invoke(self, input):
        query = input["query"]
        with self.db._engine.connect() as conn:
            result = conn.execute(text(query))
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]


def should_query(state: State):
    """Checks if the question needs a query to generate or execute"""
    prompt = (
        "You are a financial assistant."
        "Given the users question, decide weather or not if it requires querying the database"
        "if it does, respond only with 'QUERY'."
        "if it does NOT (e.g greetings, answer the question)"
        f"Question: {state['question']}\n"
    )
    response = llm.invoke(prompt)
    if response.content.strip().upper() == "QUERY":
        return "write_query"
    else:
        return "generate_answer"


def write_query(state: State):
    """Writes the query to the state."""
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system,
            ),
            (
                "human",
                "{input} id {id}",
            ),
        ]
    )
    prompt = prompt_template.invoke(
        {
            "input": state["question"],
            "id": state["id"],
            "dialect": "PostgreSQL",
            "top_k": 100,
            "table": db.get_table_info(),
        }
    )
    result = llm.with_structured_output(QueryOutput).invoke(prompt)
    return {"query": result["query"]}


def execute_query(state: State):
    """Executes the query and returns the result."""
    query = state["query"]
    query_result = QuerySQLDatabaseToolWithFields(db=db).invoke(input={"query": query})
    return {"result": query_result}


def is_encrypted(value):
    return isinstance(value, str) and value.startswith("gAAAA")


def decrypt_any_encrypted_fields(state: State):
    """Decrypts any encrypted fields in the query result."""
    for row in state["result"]:
        for key, value in row.items():
            if is_encrypted(value):
                try:
                    row[key] = security.decrypt(value)
                except Exception:
                    # Optionally log or skip if decryption fails
                    pass
    return {"result": state["result"]}


def generate_answer(state: State):
    """Generates an answer based on result"""
    prompt = (
        "You are are an agent designed to be a financial assistant. "
        "Note, for greetings, or appreciation your name is Trackify, just respond with a simple greeting or appreciation message, and asking if there is anything else you can help with"
        "Given the query, result and the question, please answer accordingly to the needs of the user in 2 to 3 sentences."
        "if the query and results are empty, just reply to the question based on the previous answer you gave the user, or if it is not associated with any previous answer, just answer the user"
        "Note, all amounts or balances are in Kobo (Or the smallest unit of the currency mostly 100 of that equals 1), and 100 Kobo is equal to 1 Naira."
        "If the User asks for any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database, "
        "just return an error message that you cannot perform such operations, Sternly warning them that if they send such messages again, the system might ban their account\n\n"
        "Also, respond in Naira, never in Kobo, or any of the smallest unit of that currency\n\n"
        f"Question: {state.get("question")}\n"
        f"Query: {state.get("query")}\n"
        f"Result: {state.get("result")}\n"
    )
    response = llm.invoke(prompt)
    return {"answer": response.content}


graph = StateGraph(State)

graph.add_node("should_query", should_query)
graph.add_node("write_query", write_query)
graph.add_node("execute_query", execute_query)
graph.add_node("decrypt_any_encrypted_fields", decrypt_any_encrypted_fields)
graph.add_node("generate_answer", generate_answer)

graph.add_conditional_edges(START, should_query)
graph.add_edge("write_query", "execute_query")
graph.add_edge("execute_query", "decrypt_any_encrypted_fields")
graph.add_edge("decrypt_any_encrypted_fields", "generate_answer")
graph.add_edge("generate_answer", END)

graph = graph.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "abc123"}}

# for step in graph.stream(
#     {
#         "question": "What bank fetches me the most money?",
#         "id": "a8da0f64-4470-457f-8564-7dacbee9cfb0",
#     },
#     config=config,
# ):
#     print(step)
