# Open Translate - Full Stack Google Colab Runner
# Repository: https://github.com/simonliu-ai-product/open-translate.git
# This script builds the frontend and runs it along with the backend on Colab.
# Everything is exposed via a single ngrok tunnel.

import os
import sys

# 1. Setup requirements
def install_dependencies():
    print("Installing system dependencies (Node.js)...")
    !curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    !sudo apt-get install -y nodejs
    print("Installing Python dependencies...")
    !pip install -q fastapi uvicorn pyngrok nest-asyncio transformers torch accelerate pillow opencc python-multipart python-dotenv bitsandbytes

# 2. Define the Backend Code
full_stack_code = """
import os
import torch
import opencc
import io
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import pipeline
from PIL import Image

app = FastAPI(title="Open Translate Full Stack")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "google/translategemma-4b-it"
converter = opencc.OpenCC('s2twp')
pipe = None

def get_pipeline():
    global pipe
    if pipe is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        print(f"Loading model {MODEL_ID} on {device}...")
        pipe = pipeline(
            "image-text-to-text",
            model=MODEL_ID,
            device=device,
            torch_dtype=dtype,
            token=HF_TOKEN,
            model_kwargs={"low_cpu_mem_usage": True}
        )
        print("Model loaded.")
    return pipe

@app.on_event("startup")
async def startup_event():
    print("Pre-loading model...")
    get_pipeline()
    print("Model standby.")

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "en"
    target_lang: str = "zh-TW"

# API Endpoints (Prefix with /api to match frontend expectations)
@app.post("/api/translate")
async def translate_text(request: TranslationRequest):
    p = get_pipeline()
    messages = [{"role": "user", "content": [{"type": "text", "source_lang_code": request.source_lang, "target_lang_code": request.target_lang, "text": request.text}]}]
    try:
        output = p(text=messages, max_new_tokens=512, generate_kwargs={"do_sample": False})
        translated_text = output[0]["generated_text"][-1]["content"]
        if "zh-TW" in request.target_lang:
            translated_text = converter.convert(translated_text)
        return {"translated_text": translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/translate-image")
async def translate_image(file: UploadFile = File(...), source_lang: str = Form("en"), target_lang: str = Form("zh-TW") ):
    p = get_pipeline()
    try:
        image = Image.open(io.BytesIO(await file.read()))
        messages = [{"role": "user", "content": [{"type": "image", "source_lang_code": source_lang, "target_lang_code": target_lang, "image": image}]}]
        output = p(text=messages, max_new_tokens=256, generate_kwargs={"do_sample": False})
        translated_text = output[0]["generated_text"][-1]["content"]
        if "zh-TW" in target_lang:
            translated_text = converter.convert(translated_text)
        return {"translated_text": translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve Frontend static files
if os.path.exists("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        return FileResponse("dist/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

def main():
    # 1. Get Tokens
    try:
        from google.colab import userdata
        hf_token = userdata.get('HF_TOKEN')
        ngrok_token = userdata.get('NGROK_TOKEN')
        os.environ["HF_TOKEN"] = hf_token
    except Exception:
        print("Error: HF_TOKEN and NGROK_TOKEN must be set in Colab Secrets.")
        return

    # 2. Install Dependencies
    install_dependencies()

    # 3. Clone repository if not exists
    if not os.path.exists("open-translate"):
        print("Cloning repository...")
        !git clone https://github.com/simonliu-ai-product/open-translate.git
        %cd open-translate
    
    # 4. Build Frontend
    print("Building frontend...")
    if os.path.exists("frontend"):
        !cd frontend && npm install && npm run build
        !cp -r frontend/dist .
    else:
        print("Warning: 'frontend' directory not found. Only API will be available.")

    # 5. Write server script
    with open("server.py", "w") as f:
        f.write(full_stack_code)

    # 6. Setup Ngrok
    from pyngrok import ngrok
    import nest_asyncio
    
    ngrok.set_auth_token(ngrok_token)
    public_url = ngrok.connect(8000).public_url
    
    print("\n" + "="*50)
    print(f"OPEN TRANSLATE UI: {public_url}")
    print("="*50)
    print("\nStarting server...")

    nest_asyncio.apply()
    !python server.py

if __name__ == "__main__":
    main()
