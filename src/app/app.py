import uvicorn
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)
from fastapi.responses import JSONResponse
import requests
from src.config.config import DEEPAI_API_KEY

app = FastAPI()

@app.post("/moderate")
async def moderate_image(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".jpg", ".png")):
        raise HTTPException(status_code=400, detail="Invalid file format")

    image_bytes = await file.read()

    try:
        response = requests.post(
            "https://api.deepai.org/api/nsfw-detector",
            headers={"api-key": DEEPAI_API_KEY},
            files={"image": (file.filename, image_bytes)}
        )
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error contacting DeepAI: {str(e)}")

    nsfw_score = data.get("output", {}).get("nsfw_score")

    if not nsfw_score:
        raise HTTPException(status_code=500, detail="No nsfw_score in response")

    if nsfw_score > 0.7:
        return JSONResponse(status_code=200, content={
            "status": "REJECTED",
            "reason": "NSFW content"
        })
    else:
        return {"status": "OK"}


if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=8000)