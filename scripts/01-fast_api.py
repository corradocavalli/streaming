import os
import uvicorn
from openai import AzureOpenAI
from dotenv import load_dotenv


from fastapi import FastAPI
from fastapi.responses import StreamingResponse


load_dotenv()
api_key=os.environ['AZURE_OPENAI_KEY']
deployment=os.environ['AZURE_OPENAI_DEPLOYMENT']
api_version=os.environ['AZURE_OPENAI_VERSION']
endpoint=os.environ['AZURE_OPENAI_ENDPOINT']

#Initialize AzureOpenAI client
client = AzureOpenAI(  
  api_key=api_key,  
  api_version = api_version
  )

# Create FastAPI app
app = FastAPI()
    
# Handles the user query and returns the response chunks
def stream_response(query: str):
    response = client.chat.completions.create(
    model=deployment,    
    messages = [
        {'role': 'system', 'content': "You are an assistant good in telling funny stories."},
        {'role': 'user', 'content': query}
        ],
    temperature=0,
    stream=True)

    for chunk in response:        
        if len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

# Define a route for the /stream URL
@app.get('/stream/')
async def stream(query: str):
    return StreamingResponse(stream_response(query), media_type='text/event-stream')

if __name__ == "__main__":    
    uvicorn.run(app, host="0.0.0.0", port=8001)