from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd

app = FastAPI()

# Allow CORS for frontend on localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load CSVs
try:
    cf_data = pd.read_csv("article_recommendations2.csv", dtype={"contentId": str})  # contentId, Recommendation 1–5
    content_data = pd.read_csv("content_filtering_results.csv", dtype={"contentId": str})  # contentId, Recommendation 1–5
    print("CSV files loaded successfully.")
except Exception as e:
    print(f"Error loading CSV files: {e}")

class RecommendationRequest(BaseModel):
    contentId: str

class RecommendationResponse(BaseModel):
    source: str
    recommendations: List[str]  # Changed to accept strings

@app.post("/recommendations/", response_model=List[RecommendationResponse])
async def get_recommendations(request: RecommendationRequest):
    contentId = request.contentId
    print(f"Received contentId: {contentId}")

    # Collaborative Filtering
    try:
        row = cf_data[cf_data["contentId"] == contentId]
        print("All available contentIds (first 10):", cf_data["contentId"].head(10).tolist())

        if row.empty:
            raise ValueError(f"No collaborative filtering data found for contentId {contentId}")
        
        rec_columns = [col for col in cf_data.columns if col.startswith("Recommendation")]
        cf_recs = row[rec_columns].values.flatten().tolist()
        cf_recs = [r if isinstance(r, str) else str(r) for r in cf_recs if pd.notna(r)]  # Keep titles as strings
    except Exception as e:
        print(f"Error getting CF recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Collaborative Filtering failed: {e}")

    # Content Filtering (commented out)
    # try:
    #     row = content_data[content_data["contentId"] == contentId]
    #     if row.empty:
    #         raise ValueError(f"No content filtering data found for contentId {contentId}")
        
    #     rec_columns = [col for col in content_data.columns if col.startswith("Recommendation")]
    #     content_recs = row[rec_columns].values.flatten().tolist()
    #     content_recs = [r if isinstance(r, str) else str(r) for r in content_recs if pd.notna(r)]  # Keep titles as strings
    # except Exception as e:
    #     print(f"Error getting content recommendations: {e}")
    #     raise HTTPException(status_code=500, detail=f"Content Filtering failed: {e}")

    return [
        {"source": "Collaborative Filtering", "recommendations": cf_recs},
        # {"source": "Content Filtering", "recommendations": content_recs},  # Commented out
        # Azure ML API can be added here later
    ]