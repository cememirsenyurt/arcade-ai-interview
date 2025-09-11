import os
import json
import hashlib
from dotenv import load_dotenv
from openai import OpenAI

# Load API key and initialize OpenAI client
load_dotenv()
client = OpenAI()

# Paths and cache setup
CACHE_FILE = ".cache/ai.jsonl"
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

# Helper function to hash prompts
def _hash_prompt(system, user):
    """Hash the system and user messages for caching."""
    payload = {"system": system, "user": user}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

# Load cache from file
def _load_cache():
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            for line in f:
                try:
                    row = json.loads(line)
                    cache[row["k"]] = row["v"]
                except Exception:
                    continue
    return cache

_cache = _load_cache()

def chat_cached(system, user, model="gpt-4o-mini"):
    """
    Get a chat completion from OpenAI, caching results to disk.
    """
    key = _hash_prompt(system, user)
    if key in _cache:
        return _cache[key]

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.4
    )
    output = response.choices[0].message.content.strip()
    with open(CACHE_FILE, "a") as f:
        f.write(json.dumps({"k": key, "v": output}) + "\n")
    _cache[key] = output
    return output