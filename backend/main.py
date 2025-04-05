from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
# import requests  # Not needed since we're disabling Azure for now

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load CSVs
try:
    cf_data = pd.read_csv("article_recommendations.csv")  # item_id, recommendations
    content_data = pd.read_csv("content_filtering_results.csv")  # item_id, recommendations
    print("CSV files loaded successfully.")
except Exception as e:
    print(f"Error loading CSV files: {e}")

class RecommendationRequest(BaseModel):
    item_id: int

class RecommendationResponse(BaseModel):
    source: str
    recommendations: List[int]

@app.post("/recommendations/", response_model=List[RecommendationResponse])
async def get_recommendations(request: RecommendationRequest):
    item_id = request.item_id
    print(f"Received item_id: {item_id}")

    # Collaborative Filtering
    try:
        cf_row = cf_data[cf_data["item_id"] == item_id]["recommendations"]
        print(f"CF row: {cf_row}")
        cf_recs = cf_row.values[0].split(",") if not cf_row.empty else []
    except Exception as e:
        print(f"Error getting CF recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Collaborative Filtering failed: {e}")

    # Content Filtering
    try:
        content_row = content_data[content_data["item_id"] == item_id]["recommendations"]
        print(f"Content row: {content_row}")
        content_recs = content_row.values[0].split(",") if not content_row.empty else []
    except Exception as e:
        print(f"Error getting content recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Content Filtering failed: {e}")

    # Azure disabled for now
    # azure_recs = []
    # try:
    #     headers = {"Authorization": f"Bearer {AZURE_API_KEY}"}
    #     payload = {
    #         "user_id": HARDCODED_USER_ID,
    #         "item_id": item_id
    #     }
    #     response = requests.post(AZURE_API_URL, json=payload, headers=headers)
    #     if response.status_code == 200:
    #         azure_recs = response.json().get("recommendations", [])
    #     else:
    #         print(f"Azure error: {response.status_code} - {response.text}")
    # except Exception as e:
    #     print(f"Azure request failed: {e}")

    return [
        {"source": "Collaborative Filtering", "recommendations": cf_recs},
        {"source": "Content Filtering", "recommendations": content_recs},
        # {"source": "Azure ML API", "recommendations": azure_recs},
    ]
