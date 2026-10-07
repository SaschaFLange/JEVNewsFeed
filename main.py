import requests
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()
TYPESAFE_API_KEY = os.getenv("TYPESAFE_API_KEY")

app = FastAPI(title="Hacker News & Jev AI Triage Backend")

# Allow Frontend (Figma exported UI / HTML) to communicate with Python server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows local HTML or local dev server to talk to FastAPI
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StoryAnalysisRequest(BaseModel):
    title: str


@app.get("/")
def read_root():
    return FileResponse("index.html")  # Serve the frontend HTML file
    #return {"status": "Python FastAPI backend is running!"}


# Endpoint 1: Fetch Live Feed Data
@app.get("/api/feed")
def get_feed():
    try:
        # Public, free Hacker News API endpoint
        url = "https://hn.algolia.com/api/v1/search?tags=front_page"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Extract top 10 stories formatted neatly for the frontend
        stories = []
        for item in data.get("hits", [])[:10]:
            stories.append(
                {
                    "id": item.get("objectID"),
                    "title": item.get("title", "No Title"),
                    "url": item.get("url", "#"),
                    "author": item.get("author", "unknown"),
                    "points": item.get("points", 0),
                }
            )

        return {"stories": stories}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch feed: {str(e)}"
        )


# Endpoint 2: Process text via Jev AI Decision Model
@app.post("/api/analyze")
def analyze_with_jev(payload: StoryAnalysisRequest):
    if not TYPESAFE_API_KEY:
        raise HTTPException(
            status_code=500, detail="TYPESAFE_API_KEY missing in .env file."
        )

    # 1. Prepare Jev AI System One question schema
    jev_payload = {
        "model": "jev-latest",
        "state": payload.title,
        "questions": {
            "category": {
                "type": "choice",
                "instructions": "Which domain best fits this headline?",
                "criteria": {
                    "engineering": "Software development, architecture, code",
                    "ai_ml": "Artificial Intelligence, LLMs, Machine Learning",
                    "business": "Startups, tech economy, funding",
                    "noise": "General off-topic or news",
                },
            },
            "hype_score": {
                "type": "score",
                "instructions": "Rate how clickbait or hyped this headline is.",
                "criteria": [
                    "Objective, calm, and informative headline",
                    "Slightly exaggerated or catchy title",
                    "Highly sensationalized clickbait or dramatic title"
                ]
            },
            "is_actionable": {
                "type": "noul",
                "instructions": "Is this useful for a software developer?",
            },
        },
    }

    # 2. Call JevStation API
    headers = {
        "Authorization": f"Bearer {TYPESAFE_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        # Endpoint for JevStation instead of TypeSafe Direct
        response = requests.post(
            "https://jevstation.com/api/v1/systemone",
            json=jev_payload,
            headers=headers,
        )

        # --- DEBUG PRINTS (LOOK AT YOUR TERMINAL) ---
        print("=== JEVSTATION API DEBUG ===")
        print("HTTP Status Code:", response.status_code)
        print("Raw Response Text:", response.text)
        print("=============================")

        response.raise_for_status()
        jev_data = response.json()

        # 3. Extract typed answers
        # Handle JevStation's {"data": {"answers": ...}} wrapper vs direct TypeSafe API
        data_block = jev_data.get("data", jev_data)
        answers = data_block.get("answers", {})

        # 1. Parse Category Choice
        category_data = answers.get("category", {})
        category_choice = category_data.get("choice", "Unknown")
        category_prob = (
            category_data.get("probabilities", {}).get(category_choice, 0.0)
        )

        # 2. Parse Hype Score
        raw_hype_score = answers.get("hype_score", {}).get("score", 0.0)
        clamped_hype = max(0.0, min(1.0, raw_hype_score))
        hype_val = round(1+(clamped_hype*9),1)

        # 3. Parse Noul (Yes/No Probability)
        actionable_data = answers.get("is_actionable", {})
        # Jev outputs Noul probabilities under the "noul" key
        noul_prob = actionable_data.get("noul", 0.0)

        return {
            "title_evaluated": payload.title,
            "decisions": {
                "category": {
                    "value": category_choice,
                    "probability": category_prob,
                },
                "hype_level": {"score": hype_val},
                "actionable": {
                    "is_actionable": noul_prob >= 0.5,
                    "probability": noul_prob,
                },
            },
        }
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502, detail=f"Jev API Request Failed: {str(e)}"
        )