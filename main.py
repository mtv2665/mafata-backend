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
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "You are Miftah Roast Engine. Return JSON with roast, score, and title."

@app.post("/unlock-shughul")
async def unlock_shughul(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        return {"roast": "يا مان، أرفع صورة حقيقية!", "score": 0, "title": "وين الصورة؟"}

    try:
        contents = await file.read()
        miftah_prompt = load_prompt()

        response = model.generate_content(
            [miftah_prompt, {"mime_type": file.content_type, "data": contents}],
            generation_config={"response_mime_type": "application/json"}
        )

        return json.loads(response.text)

    except Exception as e:
        print(f"MAFATAL_ERROR: {str(e)}") # دي حتطبع لينا العلة الحقيقية في الـ Logs
        return {
            "roast": f"الماسورة ضربت بسبب: {str(e)[:20]}...", 
            "score": 0, 
            "title": "خطأ تقني 🔧"
        }