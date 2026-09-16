import json
from pathlib import Path
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parent

REQUEST_PATH = PROJECT_ROOT / "NVDA-options-request.json"
OUTPUT_PATH = PROJECT_ROOT / "NVDA-options-response.json"

API_URL = "http://127.0.0.1:8765/api/lseg"


with REQUEST_PATH.open("r", encoding="utf-8") as file:
    request_data = json.load(file)

body = json.dumps(request_data).encode("utf-8")

request = Request(
    API_URL,
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)

print(
    f"Fetching {len(request_data['candidates'])} "
    "candidate option contracts..."
)

with urlopen(request, timeout=1800) as response:
    response_data = json.load(response)

if not response_data.get("ok"):
    raise RuntimeError(
        response_data.get("message", "LSEG option fetch failed")
    )

with OUTPUT_PATH.open("w", encoding="utf-8") as file:
    json.dump(response_data, file, indent=2)

print(f"Added contracts: {response_data.get('addedCount', 0)}")
print(f"Missing contracts: {response_data.get('missCount', 0)}")
print(f"Cached contracts: {response_data.get('contractCount', 0)}")
print(f"Saved response to: {OUTPUT_PATH}")
