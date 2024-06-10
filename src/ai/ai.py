import os
import openai
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt
import requests
import functools

load_dotenv()

GPT_MODEL_3 = "gpt-3.5-turbo-0613"
GPT_MODEL = GPT_MODEL_3
openai.api_key = os.getenv("OPEN_AI_KEY")

def consistent_twice(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        results = set()
        for i in range(5):
            res = func(*args, **kwargs)
            print(f'[SAME] {func.__name__} {res}')
            serialized_res = tuple(res) if isinstance(res, list) else res
            if serialized_res in results:
                return res
            results.add(serialized_res)
        raise Exception("Function did not produce the same result twice in 5 attempts.")
    return wrapper


@retry(wait=wait_random_exponential(multiplier=0.5, max=4), stop=stop_after_attempt(5))
def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):
    initial_timeout = 8 if model.startswith("gpt-4") else 2
    attempt = chat_completion_request.retry.statistics["attempt_number"]
    timeout_duration = initial_timeout + attempt

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key, # type: ignore
    }
    json_data = {
        "model": model,
        "temperature": 0,
        "messages": messages
    }
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
            timeout=timeout_duration,
        )
        print("-" * 50)
        return response
        
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        raise e


def pretty_print_conversation(messages):
    formatted_messages = []
    for message in messages:
        if message["role"] == "system":
            formatted_messages.append(f"system: {message['content']}\n")
        elif message["role"] == "user":
            formatted_messages.append(f"user: {message['content']}\n")
        elif message["role"] == "assistant" and message.get("function_call"):
            formatted_messages.append(f"assistant: {message['function_call']}\n")
        elif message["role"] == "assistant" and not message.get("function_call"):
            formatted_messages.append(f"assistant: {message['content']}\n")
        elif message["role"] == "function":
            formatted_messages.append(f"function ({message['name']}): {message['content']}\n")
    for formatted_message in formatted_messages:
        print(formatted_message)
