import os

import redis
from flask import Flask, jsonify, render_template, request
from logger_config import setup_logger

from rag_agent import agent_executable
from storing_documents_vectorstore import building_vectorstore

app = Flask(__name__)
redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)
redis_client.flushdb()

# Initialize logger
logger = setup_logger("my_logger")

# Example logs

main_path=os.getcwd()
faiss_path = "confluence"
if not os.path.exists(os.path.join(main_path + faiss_path)):
    print("Building vector store...")
    building_vectorstore(os.path.join(main_path + faiss_path))

agent_executor = agent_executable(os.path.join(main_path + faiss_path))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    logger.info("Processing User Question")
    try:
        data = request.json
        query = data.get("question", "")
        if not query:
            return jsonify({"error": "Empty question"}), 400

        system_prompt = "User question: "
        final_prompt = system_prompt + query

        result = agent_executor.invoke({"input": final_prompt})
        logger.debug(f"Bot result {result}")

        redis_client.rpush("chat_history", f"User: {query}")
        redis_client.rpush("chat_history", f"Bot: {result["output"]}")

        return jsonify({"answer": result["output"]})
    except Exception as e:
        logger.error(f"error occured while generating response {e}")
        return jsonify({"answer": "Error Occured."})
        
@app.route("/history", methods=["GET"])
def history():
    chat_history = redis_client.lrange("chat_history", 0, -1)
    return jsonify({"history": chat_history})


if __name__ == "__main__":
    app.run(debug=True)
