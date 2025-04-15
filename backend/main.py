from fastapi import FastAPI
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
    # Load collaborative filtering data
    cf_data = pd.read_csv("article_recommendations2.csv", dtype={"contentId": str})
    cf_data["contentId"] = cf_data["contentId"].str.strip()

    # Load content-based filtering data and fix scientific notation
    content_data = pd.read_csv("content_recommendations_titles.csv")
    content_data["contentId"] = content_data["contentId"].apply(lambda x: format(float(x), '.0f')).astype(str).str.strip()

    print("CSV files loaded successfully.")
    print("Sample CF contentIds:", cf_data["contentId"].head(5).tolist())
    print("Sample Content-based contentIds:", content_data["contentId"].head(5).tolist())
except Exception as e:
    print(f"Error loading CSV files: {e}")

class RecommendationRequest(BaseModel):
    contentId: str

class RecommendationResponse(BaseModel):
    source: str
    recommendations: List[str]

@app.post("/recommendations/", response_model=List[RecommendationResponse])
async def get_recommendations(request: RecommendationRequest):
    contentId = request.contentId.strip()
    print(f"Received contentId: '{contentId}' (type: {type(contentId)})")

    # Collaborative Filtering
    cf_recs = []
    if contentId in cf_data["contentId"].values:
        row = cf_data[cf_data["contentId"] == contentId]
        rec_columns = [col for col in cf_data.columns if col.startswith("Recommendation")]
        cf_recs = row[rec_columns].values.flatten().tolist()
        cf_recs = [r if isinstance(r, str) else str(r) for r in cf_recs if pd.notna(r)]
        print(f"CF recommendations for {contentId}: {cf_recs}")
    else:
        cf_recs = [f"No CF recommendations found for contentId {contentId}"]

    # Content Filtering
    content_recs = []
    if contentId in content_data["contentId"].values:
        row = content_data[content_data["contentId"] == contentId]
        rec_columns = [col for col in content_data.columns if col.startswith("Recommendation")]
        content_recs = row[rec_columns].values.flatten().tolist()
        content_recs = [r if isinstance(r, str) else str(r) for r in content_recs if pd.notna(r)]
        print(f"Content-based recommendations for {contentId}: {content_recs}")
    else:
        content_recs = [f"No content-based recommendations found for contentId {contentId}"]

    return [
        {"source": "Collaborative Filtering", "recommendations": cf_recs},
        {"source": "Content Filtering", "recommendations": content_recs},
    ]
