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
please, **ONLY WRITE QUERY FOR THAT USER, BASED ON THE USER'S ID BEEN PASSED, NEVER QUERY FOR ANY OTHER USER'S DATA NO MATTER THE USERS QUESTION**
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

TABLE_INFO = db.get_table_info()

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
    user_name: str
    last_query: Optional[str]
    last_answer: Optional[str]
    last_question: Optional[str]


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
    previous_question = state.get("last_question", "")
    previous_answer = state.get("last_answer", "")
    previous_query = state.get("last_query", "")
    prompt = (
        "You are a financial assistant."
        f"The previous question the user asked was {previous_question}"
        f"The previous answer the llm answered was {previous_answer}"
        "Given that information, decide whether or not the question the user now ask is query-worthy"
        "if it does, respond only with 'QUERY'."
        "if it does NOT (e.g greetings, answer the question)"
        f"Present Question: {state['question']}\n"
    )
    response = llm.invoke(prompt)
    if response.content.strip().upper() == "QUERY":
        return "write_query"
    else:
        return "generate_answer"


def write_query(state: State):
    """Writes the query to the state."""
    previous_qna = ""
    if state.get("last_question") and state.get("last_answer"):
        previous_qna = (
            f"\nPrevious question: {state['last_question']}\n"
            f"Previous answer: {state['last_answer']}\n"
        )
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system,
            ),
            (
                "human",
                "{context}" "\nCurrent question: {input} id {id}",
            ),
        ]
    )
    prompt = prompt_template.invoke(
        {
            "input": state["question"],
            "id": state["id"],
            "dialect": "PostgreSQL",
            "top_k": 100,
            "table": TABLE_INFO,
            "context": previous_qna,
        }
    )
    result = llm.with_structured_output(QueryOutput).invoke(prompt)
    return {"query": result["query"]}


def execute_query(state: State):
    """Executes the query and returns the result."""
    query = state["query"]
    query_result = QuerySQLDatabaseToolWithFields(db=db).invoke(input={"query": query})
    return {
        "result": query_result,
        "last_question": state["question"],
    }


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
    """Generates an answer based on result and past interaction if needed."""

    if not state.get("query") and not state.get("result"):
        fallback_info = (
            f"\nPrevious answer you gave was:\n{state.get('last_answer', '')}\n"
            "Try your best to answer the current question using the above info if relevant.\n"
        )
    else:
        fallback_info = ""

    prompt = (
        f"You are an AI financial assistant helping the user {state['user_name']}.\n\n"
        "Important Guidelines:\n"
        "- Always respond in a friendly and helpful manner.\n"
        "- On no account should you return the user's ID, only the name"
        "- The user has no knowledge of SQL. Do **not** use SQL terms or jargon in your responses.\n"
        "- For greetings or appreciation, simply respond as Trackify with a short, friendly message and ask if there's anything else you can help with.\n"
        "- All monetary values are stored in Kobo (the smallest unit, where 100 Kobo = 1 Naira). Always convert and respond in **Naira**.\n"
        "- If the user asks for any DML statements (e.g., INSERT, UPDATE, DELETE, DROP), respond with an error message. Warn them that continued attempts could lead to account suspension.\n"
        "Response Instructions:\n"
        "- Based on the provided query, result, and the user's question, answer clearly and helpfully in 2–3 sentences.\n"
        "- If both the query and result are empty, try to answer the question using context from your last response. If unrelated, just respond to the question as best as possible.\n\n"
        f"{fallback_info}"
        f"User Question: {state.get('question')}\n"
        f"Query: {state.get('query')}\n"
        f"Result: {state.get('result')}\n"
    )

    response = llm.invoke(prompt)
    return {
        "answer": response.content,
        "last_answer": response.content,
        "last_query": state.get("query"),  # update last_answer here
    }


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
