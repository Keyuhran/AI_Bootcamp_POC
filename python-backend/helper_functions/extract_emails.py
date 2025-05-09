import os
import json
from langchain_community.document_loaders import OutlookMessageLoader

# Dynamically resolve the path relative to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EMAIL_DIR = os.path.join(PROJECT_ROOT, "python-backend", "data", "Queries Received and Email Responses")
OUTPUT_JSONL = os.path.join(PROJECT_ROOT, "email_finetune_raw.jsonl")

SYSTEM_PROMPT = "You are a PUB assistant generating standardized, formal, confident water quality email replies."

formatted_records = []

for filename in os.listdir(EMAIL_DIR):
    if not filename.lower().endswith(".msg"):
        continue

    file_path = os.path.join(EMAIL_DIR, filename)
    
    try:
        loader = OutlookMessageLoader(file_path)
        docs = loader.load()
        if not docs or not docs[0].page_content.strip():
            continue

        email_body = docs[0].page_content.strip()

        formatted = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "USER QUERY PLACEHOLDER"},
                {"role": "assistant", "content": email_body}
            ]
        }

        formatted_records.append(formatted)
    except Exception as e:
        print(f"⚠️ Failed to load {filename}: {e}")

with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
    for record in formatted_records:
        json.dump(record, f)
        f.write("\n")

print(f"✅ Extracted {len(formatted_records)} records to {OUTPUT_JSONL}")
