### First, run the docker container, or if it's not created run this code:
docker run -d --name qdrant -p 6333:6333 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant

### Then start the main app using this code:
uv run uvicorn main:app

### Finally start the local qdrant server:
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery

### To open the frontend interface using streamlit, run this code:
uv run streamlit run .\streamlit_app.py

***(Remember to get your gemini or openai key and put it in the .env file)***