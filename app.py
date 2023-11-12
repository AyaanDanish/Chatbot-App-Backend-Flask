from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Set up Azure OpenAI configuration
openai.api_type = "azure"
openai.api_version = "2023-08-01-preview"
openai.api_base = os.environ.get("API_BASE")
openai.api_key = os.environ.get("API_KEY")
deployment_id = os.environ.get("DEPLOYMENT_ID")

search_endpoint = os.environ.get("SEARCH_ENDPOINT")
search_key = os.environ.get("SEARCH_KEY")
search_index_name = os.environ.get("SEARCH_INDEX_NAME")


def setup_byod(deployment_id: str) -> None:
    """Sets up the OpenAI Python SDK to use your own data for the chat endpoint.

    :param deployment_id: The deployment ID for the model to use with your own data.

    To remove this configuration, simply set openai.requestssession to None.
    """

    class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):
        def send(self, request, **kwargs):
            request.url = f"{openai.api_base}/openai/deployments/{deployment_id}/extensions/chat/completions?api-version={openai.api_version}"
            return super().send(request, **kwargs)

    session = requests.Session()

    session.mount(
        prefix=f"{openai.api_base}/openai/deployments/{deployment_id}",
        adapter=BringYourOwnDataAdapter(),
    )

    openai.requestssession = session


@app.route("/send_to_backend", methods=["POST"])
def send_to_backend():
    data = request.json
    user_input = data.get("userMsg")

    # Build conversation
    conversation = [{"role": "user", "content": user_input}]

    setup_byod(deployment_id)

    completion = openai.ChatCompletion.create(
        messages=conversation,
        deployment_id=deployment_id,
        dataSources=[
            {
                "type": "AzureCognitiveSearch",
                "parameters": {
                    "endpoint": search_endpoint,
                    "key": search_key,
                    "indexName": search_index_name,
                },
            }
        ],
    )

    response_content = completion["choices"][0]["message"]["content"]

    return jsonify({"response": response_content})


if __name__ == "__main__":
    app.run(debug=True)
