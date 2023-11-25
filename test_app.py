import pytest
from flask import Flask
from app import app, chat
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_favicon(client):
    response = client.get('/favicon.ico')
    assert response.status_code == 200
    assert response.mimetype == 'image/vnd.microsoft.icon'

def test_chat(client):
    data = {
        "userMsg": "Hello",
        "conversation": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            }
        ]
    }
    response = client.post('/send_to_backend', json=data)
    assert response.status_code == 200
