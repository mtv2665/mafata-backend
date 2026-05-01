import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

app = FastAPI(title="Miftah_Backend")

# 1. Security Check: Explicitly check for GEMINI_API_KEY
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY environment variable not set. API calls will fail.")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Configure strict CORS for the Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
        # Add production domain here later, e.g., "https://miftah.app"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Double Entendre Logic: Read the prompt directly from the file
def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "You are Miftah Roast Engine. Return JSON with roast, score, and title."

@app.post("/unlock-shughul")
async def unlock_shughul(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Ya man, upload a photo!")

    try:
        # 3. Data Handling: Read into memory and close immediately to ensure privacy
        contents = await file.read()
        await file.close() # Explicitly close the file
        
        mime_type = file.content_type
        miftah_prompt = load_prompt()

        # Call Gemini Vision API
        response = model.generate_content(
            [
                miftah_prompt,
                {"mime_type": mime_type, "data": contents}
            ],
            generation_config={"response_mime_type": "application/json"}
        )

        # 4. Output Integrity: Parse JSON and ensure fields exist
        result_content = response.text
        result_dict = json.loads(result_content)
        
        # Ensure fallback values if the AI misses something
        return {
            "roast": result_dict.get("roast", "الـ AI صام، ملامحك صدمتو"),
            "score": result_dict.get("score", 0),
            "title": result_dict.get("title", "فحص غامض"),
            "share_text": result_dict.get("share_text", "خش شوف الشغل ده! 🔥")
        }

    except Exception as e:
        print(f"Error during AI processing: {e}")
        # Error Handling: Return the street-style error message
        return {
            "roast": "الماسورة ضربت، السيرفر ده محتاج عمرة", 
            "score": 0, 
            "title": "خطأ تقني 🔧",
            "share_text": "السيرفر طار، دعواتك! 🚀"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
