
# Custm OpenAI API Proxy Server

This is a simple proxy server for an OpenAI-compatible API. It allows you to route requests to another OpenAI-style server (like Gemma or DeepSeek) and provides basic authentication.  It's designed to be easily customizable with your own API keys, target URL, and model IDs.

## Introduction

This project acts as a middleman between clients and an OpenAI-compatible backend. This can be useful for:

* **Routing requests:** Directing traffic to different models or servers based on your needs.
* **Authentication:** Adding an extra layer of authentication before requests reach the backend.
* **Customization:** Modifying requests or responses as needed.
* **Testing:**  Easily switch between different backends for A/B testing.

## Installation

1.  **Install dependencies:**

    ```bash
    pip install fastapi uvicorn openai
    ```

## Configuration

The following variables in the code need to be configured:

*   `DASHSCOPE_API_KEY`: The API key for your target OpenAI-style server (e.g., Gemma, DeepSeek).  This is the key used when making requests *to* the backend server.
*   `URL`: The base URL of your target OpenAI-style server. For example: `http://127.0.0.1:1234/v1/`.
*   `TARGET_MODEL`:  The ID of the model you want this proxy to use on the backend server (e.g., "gemma1b").
*   `VERIFY_API_KEY`: The API key that clients need to provide when connecting *to* this proxy server for authentication.

## Usage

1.  **Run the server:**

    ```bash
    python app.py
    ```

    This will start the server on `http://0.0.0.0:8000`.

2.  **Send requests:**

    Clients can send OpenAI-compatible API requests to `http://0.0.0.0:8000/v1/chat/completions` (or other supported endpoints).  They need to include the `VERIFY_API_KEY` in the `Authorization` header as a Bearer token:  Currently default VERIFY_API_KEY is 123456.

## API Endpoints

*   **`/v1/models` (GET):** Returns a list of supported models. Currently returns a fake model list containing only `TARGET_MODEL`.
*   **`/v1/chat/completions` (POST):**  The main endpoint for chat completions. Accepts a JSON payload similar to the OpenAI Chat Completions API. Supports both streaming and non-streaming responses.

## Example Request (Streaming)

```json
{
    "model": "deepseekqwen7bq8",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Introduce yourself"}
    ],
    "temperature": 0.7,
    "top_p": 1,
    "stream": true
}
```

## Example Response (Streaming)

The response will be a `text/event-stream` with each chunk formatted as:

```
data: {"id": "chatcmpl-123", "object": "chat.completion.chunk", "created": 1687000000, "model": "gemma1b", "choices": [{"index": 0, "delta": {"content": "Hello!"}, "finish_reason": null}]}
```

The stream ends with:

```
data: [DONE]
```

## Key Features

*   **Streaming Support:**  Handles both streaming and non-streaming chat completion requests.
*   **Authentication:** Requires a `VERIFY_API_KEY` for client access.
*   **Customizable:** Easily configurable API key, URL, and model ID.
*   **Simple Implementation:**  Easy to understand and modify.

## Future Enhancements

*   **More robust error handling.**
*   **Support for more OpenAI API endpoints. Needs to support /v1/comletions and /v1/embeddings in the future.**
*   **Configuration via environment variables or a config file.**
*   **Logging and metrics.**

Author: Forsakensilver
