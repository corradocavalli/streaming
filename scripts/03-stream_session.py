# region [Initialization...]
import asyncio
import os
import uvicorn

from openai import AzureOpenAI
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from streaming_session import StreamingSession


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
# endregion

# Load RAG documents
def load_documents(session: StreamingSession):    
    for i in range(1, 5):
        session.write_message(f"Loading document {i}\n")
    
# Handles the user query and returns the response chunks
def call_llm(query: str, session: StreamingSession):    
    session.write_message("Hey there! I am your AI assistant.\n")
    
    load_documents(session)
    
    try:
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
                    session.write_message(delta.content)
        
        session.close()
                    
    except Exception as e:
        session.write_error(f"An error occurred: {str(e)}")
        
async def stream_response(query: str):    
    # creates the session communication channel shared between the LLM task and the dequeuer
    streaming_session = StreamingSession()
    asyncio.create_task(asyncio.to_thread(call_llm, query, streaming_session))
 
    # Dequeues the messages queued by call_llm until the session is closed
    while True:
        data = streaming_session.read()
        if data:
            if data == StreamingSession.STOP:                
                break
            else:
                yield data
 
        await asyncio.sleep(0.01)

# Define a route for the /stream URL
@app.get('/stream/')
async def stream(query: str):
    return StreamingResponse(stream_response(query), media_type='text/event-stream')

if __name__ == "__main__":    
    uvicorn.run(app, host="0.0.0.0", port=8001)