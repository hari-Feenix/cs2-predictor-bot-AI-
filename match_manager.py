import openai
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import random

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

MATCH_DB = 'data/matches.json'

def _load_matches():
    try:
        with open(MATCH_DB, 'r') as f:
            return json.load(f)
    except:
        return []

def _save_matches(matches):
    with open(MATCH_DB, 'w') as f:
        json.dump(matches, f, indent=2)

def get_upcoming_matches():
    matches = _load_matches()
    if not matches:
        prompt = "Generate 5 upcoming professional Counter-Strike 2 matches. Include match_id, time (UTC, format %Y-%m-%d %H:%M:%S), team1, and team2. Format as JSON."
       client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)

        matches = eval(response['choices'][0]['message']['content'])
        _save_matches(matches)
    return matches

def resolve_matches():
    matches = _load_matches()
    now = datetime.utcnow()
    resolved = []
    unresolved = []

    for match in matches:
        match_time = datetime.strptime(match['time'], '%Y-%m-%d %H:%M:%S')
        if match_time <= now:
            winner = random.choice([match['team1'], match['team2']])
            match['winner'] = winner
            resolved.append(f"Match {match['match_id']} is over! Winner: **{winner}**")
            from prediction_manager import finalize_predictions
            finalize_predictions(match['match_id'], winner)
        else:
            unresolved.append(match)

    _save_matches(unresolved)
    return resolved
