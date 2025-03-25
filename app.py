#py -3.12 -m pip install fastapi
#py -3.12 -m pip install uvicorn
#py -3.12 -m pip install openai
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json
import time
import uvicorn
import openai
import openai.types.chat.chat_completion

# A basic openapi proxy server, you can modifiy the code to adapt your own custom api keys, etc.

app = FastAPI()

DASHSCOPE_API_KEY = 'your-api-key'  # actual openai api style server's api key
URL = 'http://127.0.0.1:1234/v1/'  # change to actual openai api style server url 
TARGET_MODEL = "gemma1b"  # target model id, the model you want your proxy server to call

VERIFY_API_KEY = '123456'  # api key required for the client to connect to this proxy server

FAKE_MODELS = {
    "object": "list",
    "data": [
        {
            "id": TARGET_MODEL,
            "object": "model",
            "created": 1686935002,
            "owned_by": "my-org"
        },
    ]
}


client = openai.OpenAI(
    api_key = DASHSCOPE_API_KEY,
    base_url= URL
)

def simple_response(input_text):
    return {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": TARGET_MODEL,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": input_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }

@app.get("/v1/models")
async def get_models():
    return FAKE_MODELS

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        
        data = await request.json()
        print(f"Received header:{request.headers}")
        authorization = request.headers.get("authorization")
        #Example Bearer 11111111
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            #verify client's api key
            if token != VERIFY_API_KEY:
                return simple_response("Invalid token")
        else:
            return simple_response("Invalid token")
        print(f"Received:{data}")
        #Received:{'messages': 
        # [{'role': 'system', 'content': '\nCurrent model: deepseekqwen7bq8\nCurrent date: 2025-03-25T03:21:02.147Z\n\nYou are a helpful assistant.'}, 
        # {'role': 'user', 'content': 'Introduce your self'}], 
        # 'model': 'deepseekqwen7bq8', 'temperature': 0.7, 'top_p': 1, 'stream': True}
        stream = data.get("stream", False)
    except Exception as e:
        stream = False
        print(f"Invalid request:{e}")
        return simple_response("Invalid token")

    if stream:
        def generate_stream_response():
            model = TARGET_MODEL
            messages = data.get("messages", [])
            temperture = data.get("temperature", 0.7)
            top_p = data.get("top_p", 1)
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=temperture,
                top_p=top_p
            )
            for chunk in response:
                # print usage if usage is on
                if not chunk.choices:
                    print("\nUsage:")
                    print(chunk.usage)
                else:
                    delta = chunk.choices[0].delta
                    chunk = {
                        "id": "chatcmpl-123",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": TARGET_MODEL,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": delta.content},
                                "finish_reason": None
                            }
                        ]
                    }
                    yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_stream_response(),
            media_type="text/event-stream"
        )
    else:
        model = TARGET_MODEL
        messages = data.get("messages", [])
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
