# RAG App run locally

### First, run the docker container, or if it's not created run this code:
docker run -d --name qdrant -p 6333:6333 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant

### Then start the main app using this code:
uv run uvicorn main:app

### Finally start the local qdrant server:
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery

### To open the frontend interface using streamlit, run this code:
uv run streamlit run .\streamlit_local_app.py

# RAG App run on Streamlit Cloud

### Setup a Streamlit Cloud app
Copy your .env file to the toml in Advanced Settings
```
GEMINI_API_KEY="AIzaSyAXgHTIloP_ZeyhltRbeIDAKK-66KRVSQ8"
QDRANT_URL="https://1430fa95-5e8c-4aad-a7c8-a4dbbe540eb6.us-east-1-1.aws.cloud.qdrant.io"
QDRANT_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.LcuqPp38mc6-UjJtFLiSImlMS2I0hn9M8yJ-CdYO_jE"
```

Then select the master branch and the streamlit_cloud_app.py file to initialize the app.

***(Remember to get your gemini or openai key and put it in the .env file)***
