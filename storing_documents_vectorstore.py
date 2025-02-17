import pickle

from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import FAISS

from data_from_confluence import take_data_from_confluence, take_data_from_pages
from logger_config import setup_logger

# Initialize logger
logger = setup_logger("my_logger")


load_dotenv()

import os

os.environ.get("OPENAI_API_KEY")
# Initialize the embedding model (Replace with your API key if required)
embeddings = OpenAIEmbeddings()


def process_data(table, plain_text, attachments):

    logger.info("Processing data for vector Store")
    documents = []

    for record in table:
        page_content = str(record)
        metadata = {k: v for k, v in record.items() if k != "text"}
        documents.append(Document(page_content=page_content, metadata=metadata))

    for record in plain_text:
        documents.append(
            Document(
                page_content=record["text"],
                metadata={k: v for k, v in record.items() if k != "text"},
            )
        )

    for record in attachments:
        documents.append(
            Document(
                page_content=record["text"],
                metadata={k: v for k, v in record.items() if k != "text"},
            )
        )

    return documents


def building_vectorstore(faiss_path):
    logger.info("Creating vector-store")

    try:
        confluence, pages = take_data_from_confluence()
        all_tables, all_text_data, all_attachments = take_data_from_pages(
            confluence, pages
        )

        documents = process_data(all_tables, all_text_data, all_attachments)
        vector_store = FAISS.from_documents(documents, embeddings)

        # Save the vector store
        vector_store.save_local(faiss_path)
        return True
    except Exception as e:
        logger.error(f"Error occured while creating vector-store {e}")

        return False


def load_vector_store(faiss_path):
    logger.info("Loading vector-store")
    try:
        # Load the vector store later
        retrieved_store = FAISS.load_local(
            faiss_path, embeddings, allow_dangerous_deserialization=True
        )
        return retrieved_store
    except Exception as e:
        logger.error(f"Error occured while loading vector-store {e}")

    return None
