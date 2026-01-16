import os
import torch
import opencc
import io
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
from PIL import Image
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Database imports
from . import models, database

load_dotenv()

# Initialize Database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Open Translate API (TranslateGemma)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = os.getenv("MODEL_ID", "google/translategemma-4b-it")

# Initialize OpenCC for Simplified to Traditional Chinese conversion
converter = opencc.OpenCC('s2twp')

# Global pipeline
pipe = None

def get_pipeline():
    global pipe
    if pipe is None:
        if not HF_TOKEN:
            print("Warning: HF_TOKEN is not set. You might not be able to download the model.")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Using bfloat16 for better precision if CUDA is available
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        
        print(f"Loading model {MODEL_ID} on {device}...")
        try:
            pipe = pipeline(
                "image-text-to-text",
                model=MODEL_ID,
                device=device,
                torch_dtype=dtype,
                token=HF_TOKEN,
                model_kwargs={
                    "low_cpu_mem_usage": True,
                }
            )
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e
    return pipe

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "en"
    target_lang: str = "zh-TW"

@app.on_event("startup")
async def startup_event():
    # Load model on startup and keep it in memory
    print("Pre-loading model during startup...")
    try:
        get_pipeline()
        print("Model is ready and standby.")
    except Exception as e:
        print(f"Startup error: Could not load model. {e}")

@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": pipe is not None}

@app.post("/translate")
async def translate_text(request: TranslationRequest, db: Session = Depends(database.get_db)):
    p = get_pipeline()
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "source_lang_code": request.source_lang,
                    "target_lang_code": request.target_lang,
                    "text": request.text,
                }
            ],
        }
    ]
    
    try:
        output = p(text=messages, max_new_tokens=512, generate_kwargs={"do_sample": False})
        translated_text = output[0]["generated_text"][-1]["content"]
        
        if request.target_lang in ["zh-TW", "zh_TW", "zh-Hant"]:
            translated_text = converter.convert(translated_text)
            
        # Log to Database
        log_entry = models.TranslationLog(
            source_text=request.text,
            translated_text=translated_text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            translation_type="text"
        )
        db.add(log_entry)
        db.commit()
            
        return {"translated_text": translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate-image")
async def translate_image(
    file: UploadFile = File(...),
    source_lang: str = Form("en"),
    target_lang: str = Form("zh-TW"),
    db: Session = Depends(database.get_db)
):
    p = get_pipeline()
    
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source_lang_code": source_lang,
                        "target_lang_code": target_lang,
                        "image": image,
                    },
                ],
            }
        ]
        
        output = p(text=messages, max_new_tokens=256, generate_kwargs={"do_sample": False})
        translated_text = output[0]["generated_text"][-1]["content"]
        
        if target_lang in ["zh-TW", "zh_TW", "zh-Hant"]:
            translated_text = converter.convert(translated_text)
            
        # Log to Database
        log_entry = models.TranslationLog(
            image_name=file.filename,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            translation_type="image"
        )
        db.add(log_entry)
        db.commit()
            
        return {"translated_text": translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history(limit: int = 10, db: Session = Depends(database.get_db)):
    logs = db.query(models.TranslationLog).order_by(models.TranslationLog.created_at.desc()).limit(limit).all()
    return logs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
