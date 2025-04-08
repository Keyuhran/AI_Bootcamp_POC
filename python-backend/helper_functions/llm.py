import os
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken

import asyncio

load_dotenv('.env')

# Load APIKey into OpenAI Model
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Helper Function 1 : Generate Embedding
def get_embedding(input, model='text-embedding-3-small'):
    response = client.embeddings.create(
        input=input,
        model=model
    )
    return [x.embedding for x in response.data]

# Helper Function 2 : Call out LLM
def get_completion(prompt, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1, json_output=False):
    if json_output == True:
      output_json_structure = {"type": "json_object"}
    else:
      output_json_structure = None

    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create( #originally was openai.chat.completions
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=1,
        response_format=output_json_structure,
    )
    return response.choices[0].message.content

# Note that this function directly take in "messages" as the parameter.
def get_completion_by_messages(messages, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1, json_output=False):
    if json_output == True:
      output_json_structure = {"type": "json_object"}
    else:
      output_json_structure = None

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=1,
        response_format=output_json_structure
    )
    return response.choices[0].message.content

# Define async version of the get_completion_by_messages
async def get_completion_by_messages_async(messages, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1, json_output=False):
    if json_output:
        output_json_structure = {"type": "json_object"}
    else:
        output_json_structure = None

    response = await client.chat.completions.acreate(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=n,
        response_format=output_json_structure
    )
    return response.choices[0].message.content

# Helper Function 3 : Calculating the tokens given the "message"
# ⚠️ This is simplified implementation that is good enough for a rough estimation
def count_tokens(text):
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    return len(encoding.encode(text))


def count_tokens_from_message(messages):
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    value = ' '.join([x.get('content') for x in messages])
    return len(encoding.encode(value))