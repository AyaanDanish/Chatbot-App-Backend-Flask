from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import tiktoken
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

openai.api_type = "azure"
openai.api_version = "2023-08-01-preview"
openai.api_base = os.environ.get("API_BASE")
openai.api_key = os.environ.get("API_KEY")
deployment_id = os.environ.get("DEPLOYMENT_ID")

max_response_tokens = 250
token_limit = 4000


def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for message in messages:
        num_tokens += (
            4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        )

        for key, value in message.items():
            if value != None:
                num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens


# Sends a message to the backend
@app.route("/send_to_backend", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("userMsg")
    conversation = data.get(
        "conversation", [{"role": "system", "content": "You are a helpful assistant."}]
    )

    conversation.append({"role": "user", "content": user_input})

    num_tokens = num_tokens_from_messages(conversation)
    while num_tokens + max_response_tokens >= token_limit:
        del conversation[1]
        num_tokens = num_tokens_from_messages(conversation)

    response = openai.ChatCompletion.create(
        engine="myassist-model",
        messages=conversation,
        temperature=0.7,
        max_tokens=token_limit,
    )

    conversation.append(
        {"role": "assistant", "content": response["choices"][0]["message"]["content"]}
    )

    return jsonify(conversation)


if __name__ == "__main__":
    app.run(debug=True)

