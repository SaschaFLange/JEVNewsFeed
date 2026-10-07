# ⚡ Hacker News & Jev AI Content Triager

A lightweight, zero-cost decision intelligence web application that ingests real-time front-page articles from Hacker News and processes them through **Jev AI (TypeSafe AI System One Engine)** to perform automated content triage and classification.

---

## 🛠️ Tech Stack

- **Backend:** Python (FastAPI, Uvicorn)
- **Frontend:** HTML5, JavaScript (Fetch API), Tailwind CSS
- **Decision Engine:** Jev AI / TypeSafe System One (via JevStation API)
- **Data Source:** Hacker News Algolia Search API

---

## ✨ Features

- **Live Data Ingestion:** Fetches real-time front-page stories, scores, authors, and URLs from Hacker News without requiring auth or API keys.
- **Typed AI Decision Triage:** Evaluates headlines using Jev AI's structured decision outputs:
  - **Category Classification (`Choice`):** Classifies titles into domain buckets (*Engineering, AI/ML, Business, Noise*).
  - **Hype Score Analysis (`Score`):** Maps title sensationalism along probability density curves scaled to a clean 1.0–10.0 Hype Rating (*Calm, Catchy, Clickbait*).
  - **Actionability Assessment (`Noul`):** Returns calibrated boolean probabilities evaluating whether an article is directly actionable for software engineers.
- **Responsive Dashboard:** Simple, fast Tailwind UI designed for rapid manual or automated content evaluation.

---

## 📂 Project Structure

```text
my-ai-app/
├── main.py           # FastAPI backend routes & Jev AI schema integrations
├── index.html        # Responsive frontend UI served directly by FastAPI
├── .env              # Environment variables (API keys - excluded from Git)
├── .gitignore        # Git ignore rules
└── README.md         # Project documentation
```
---

## Quick Start & Local Setup
1. Clone the Repository
```bash
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name
```

2. Set Up Virtual Environment & Install Dependencies
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

pip install fastapi uvicorn requests python-dotenv
```

3. Configure API Credentials

Create a .env file in the root directory:
Code-Snippet

```bash
TYPESAFE_API_KEY=your_jevstation_api_key_here
```

4. Run the Application

Start the Uvicorn web server:

```bash
uvicorn main:app --reload
```

Open your browser and visit http://127.0.0.1:8000/ to interact with the dashboard.

🔬 Jev AI Decision Schema

The application submits structured decision payloads to JevStation using the following schema format:
JSON

```json
{
  "model": "jev-latest",
  "state": "Article Title Here",
  "questions": {
    "category": {
      "type": "choice",
      "instructions": "Which domain best fits this headline?",
      "criteria": {
        "engineering": "Software development, architecture, code",
        "ai_ml": "Artificial Intelligence, LLMs, Machine Learning",
        "business": "Startups, tech economy, funding",
        "noise": "General off-topic news"
      }
    },
    "hype_score": {
      "type": "score",
      "instructions": "Rate sensationalism along this spectrum.",
      "criteria": [
        "Objective, calm, and informative headline",
        "Slightly exaggerated or catchy title",
        "Highly sensationalized clickbait or dramatic title"
      ]
    },
    "is_actionable": {
      "type": "noul",
      "instructions": "Is this useful for a developer?"
    }
  }
}
```

📄 License

MIT
