import requests
r = requests.post(
    'https://rel.cs.ru.nl/api',
    json={"text": "The capital of France is Paris", "spans": []},
    headers={"Content-Type": "application/json"},
    timeout=30
)
print(r.status_code)
print(r.json())
