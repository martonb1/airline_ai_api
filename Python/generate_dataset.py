import os
import sys
import json
import csv
import subprocess
import random
from pathlib import Path

API_KEY = "sk-"


# Ensure 'openai' is installed for this interpreter
try:
    from openai import OpenAI
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    from openai import OpenAI

AIRLINES = ["EVA Air", "Starlux", "China Airlines", "Tigerair Taiwan"]
MODEL = "gpt-4o-mini"
TARGET_ROWS = 100
OUT_CSV = "airline_dataset.csv"


def require_key():
    if not API_KEY or API_KEY.startswith("sk-REPLACE"):
        print("ERROR: Put your real API key into API_KEY.", file=sys.stderr)
        sys.exit(1)
    return API_KEY


def build_prompt():
    return f"""
Return ONLY valid JSON as:
{{"rows":[{{"airline": str, "route": "domestic"|"international",
"flight_hours": number, "energy_consumption_mwh": number,
"passenger_load": integer, "co2_emissions_tonnes": number}} ...]}}

Rules:
- Try to output {TARGET_ROWS} objects in "rows".
- "airline" ∈ {AIRLINES}. Tigerair Taiwan must be international only.
- "route": domestic is rare; most are international.
- "flight_hours": domestic ~0.5–1.5; international ~2–6 (regional) or 8–13 (long-haul).
- "energy_consumption_mwh" ~ proportional to flight_hours.
- "passenger_load": domestic 80–160; regional 120–260; long-haul 220–360.
- "co2_emissions_tonnes" correlates with energy_consumption_mwh.
- Numbers must be numeric (not strings). No explanations—JSON only.
"""


def call_api():
    client = OpenAI(api_key=require_key())
    resp = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        temperature=0.2,
        messages=[
            {"role": "system", "content": "You are a strict JSON generator for data analysis demos."},
            {"role": "user", "content": build_prompt()},
        ],
    )
    return resp.choices[0].message.content


def parse_and_pad(text):
    data = json.loads(text)
    rows = data.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError("Model did not return JSON with a 'rows' array.")
    if len(rows) == 0:
        raise ValueError("Model returned zero rows.")
    # If fewer than TARGET_ROWS, duplicate random rows until length is met
    while len(rows) < TARGET_ROWS:
        rows.append(random.choice(rows))
    # If more, truncate
    rows = rows[:TARGET_ROWS]
    # Normalize/cast types
    cleaned = []
    for x in rows:
        cleaned.append({
            "airline": str(x["airline"]),
            "route": str(x["route"]),
            "flight_hours": float(x["flight_hours"]),
            "energy_consumption_mwh": float(x["energy_consumption_mwh"]),
            "passenger_load": int(x["passenger_load"]),
            "co2_emissions_tonnes": float(x["co2_emissions_tonnes"]),
        })
    return cleaned


def write_csv(rows, out_path: Path):
    headers = ["airline", "route", "flight_hours",
               "energy_consumption_mwh", "passenger_load", "co2_emissions_tonnes"]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)


def main():
    print(f"Calling {MODEL}… aiming for {TARGET_ROWS} rows")
    json_text = call_api()
    rows = parse_and_pad(json_text)
    out_path = Path(__file__).parent / OUT_CSV
    write_csv(rows, out_path)
    print(f"Done → {out_path} (rows: {len(rows)})")


if __name__ == "__main__":
    main()
