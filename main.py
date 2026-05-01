import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

app = FastAPI(title="Miftah_Backend")

# إعداد الـ CORS - الحل السحري لمشكلة Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return "You are Miftah Roast Engine. Return JSON with roast, score, title, and share_text."

@app.post("/unlock-shughul")
async def unlock_shughul(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        return {"roast": "يا مان، أرفع صورة حقيقية!", "score": 0, "title": "وين الصورة؟", "share_text": ""}

    try:
        contents = await file.read()
        miftah_prompt = load_prompt()
        
        models_to_try = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-pro-vision"]
        response_text = None
        last_error = None

        for model_name in models_to_try:
            try:
                # Dynamic Prompt Loading via system_instruction
                model = genai.GenerativeModel(
                    model_name,
                    system_instruction=miftah_prompt
                )
                
                response = model.generate_content(
                    [{"mime_type": file.content_type, "data": contents}],
                    generation_config={"response_mime_type": "application/json"}
                )
                response_text = response.text
                break # Success, exit the loop
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                last_error = e
                continue

        if not response_text:
            raise last_error or Exception("All models failed")

        return json.loads(response_text)

    except Exception as e:
        error_msg = str(e)
        print(f"MAFATAL_ERROR: {error_msg}") # Logging the real error
        
        # Enhanced Error Handling Fallback
        return {
            "roast": f"الماسورة ضربت بسبب: {error_msg[:40]}...", 
            "score": 0, 
            "title": "خطأ تقني 🔧",
            "share_text": "السيرفر طار، دعواتك! 🚀"
        }