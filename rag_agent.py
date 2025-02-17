import os

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import (
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from logger_config import setup_logger

# Initialize logger
logger = setup_logger("my_logger")


load_dotenv()


os.environ.get("OPENAI_API_KEY")
# Initialize the embedding model (Replace with your API key if required)


def build_retrieval_tool(faiss_path):
    logger.info("Creating Tool for Agent")
    # Example logs
    try:
        embeddings = OpenAIEmbeddings()

        retrieved_store = FAISS.load_local(
            faiss_path, embeddings, allow_dangerous_deserialization=True
        )
        retriever = retrieved_store.as_retriever()

        retriever_tool = create_retriever_tool(
            retriever=retriever,
            name="faiss_retriever",
            description="Retrieve documents from FAISS store",
        )

        return retriever_tool
    except Exception as e:
        logger.error(f"Error occurred while creating tool: {e}")


def rag_agent_prompt():

    # Define the main prompt structure
    chat_history_placeholder = MessagesPlaceholder(
        variable_name="chat_history", optional=True
    )
    user_message_template = HumanMessagePromptTemplate(
        prompt=PromptTemplate(input_variables=["input"], template="{input}")
    )
    agent_scratchpad_placeholder = MessagesPlaceholder(variable_name="agent_scratchpad")

    # System message introducing the agent
    intro_prompt = SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=[],
            template="You are a helpful assistant.Searches and returns the best answer to user question",
        )
    )

    # Combine all elements into the final prompt
    final_prompt = (
        intro_prompt
        + chat_history_placeholder
        + user_message_template
        + agent_scratchpad_placeholder
    )
    return final_prompt


def agent_executable(
    faiss_path,
):
    logger.info("Creating Agent")
    try:
        llm = ChatOpenAI()

        retriever_tool = build_retrieval_tool(faiss_path)

        tools = [retriever_tool]

        rag_agent = initialize_agent(
            tools, llm, agent="zero-shot-react-description", verbose=True
        )
        prompt = rag_agent_prompt()

        rag_agent = create_openai_tools_agent(llm, tools, prompt)

        agent_executor = AgentExecutor(agent=rag_agent, tools=tools, verbose=True)
        return agent_executor
    except Exception as e:
        logger.error(f"Error occured while Creating Agent {e}")
