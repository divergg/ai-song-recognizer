# Ai song recognizer

## Tech stack

1) FastApi
2) OpenAi
3) RabbitMq
4) MongoDb
5) websockets, restApi
6) https://api.lyrics.ovh/v1 - used for lyrics retrieval

## How to launch
1) Set up your env vars (see env.example)
2) docker compose up

## Endpoints
Include "Authorization: Bearer {token}" in headers for all requests

### 1. Health Check

- **Endpoint:** `/health`
- **Method:** `GET`
- Response
  ```json
  {
    "status": "ok"
  }
  ```

### 2. Get websocket url

- **Endpoint:** `/ws_auth`
- **Method:** `POST`
- **Description:** Retrieve the url for websocket connection.
- **Request Body:**
  - `user_id`: *string* - Identifier of the user .
  - `chat_id`: *string* - Identifier of the chat.
- **Response:**
  - **200 OK** - Successfully retrieved scenarios.
    ```json
    {
    "ws_url": "/ws/{chat_id}"
    }
    ```
  - **400 Bad Request** - Error due to invalid input.
  - **500 Internal Server Error** - Server-side error.

### 3. Websocket endpoint

- **Endpoint:** `/ws/{chat_id}`
- **Method:** `websocket`
- **Description:** Send message for recognition.
- **Request Body:**
    ```json
    {
        "title": "string", song title
        "artist": "string", artist
        "id": "sting", id of message
        "method": "recognizeSong" identifier of method
    }
    ``
- **Response:**
  - **200 OK** - Successfully retrieved scenarios.
    ```json
    {
    "type": "event",
    "event": "newMessage",
    "data": {
        "id": "f72b339c-50bb-4983-bd33-1042a77bf58c",
        "datetime": "2025-03-12T19:29:08.734108Z",
        "user_message_id": "1",
        "text": "The song expresses longing and unresolved feelings after years of separation.",
        "countries": []
    }
    }
    ```


## Project structure
1) Api - service that receives external messages (fastApi app with websocket support and mongoDb cache for songs that were already requested)
2) worker - openai engine (based in Autogen library) that analyses users requests
3) rabbitMq - message broker between worker and api
4) MongoDb - storage of previous results (for tokens saving)