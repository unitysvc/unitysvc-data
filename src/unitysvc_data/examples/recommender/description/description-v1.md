## Recommendations via UnitySVC

Personalized recommendations powered by a Gorse-shaped engine,
fronted by the UnitySVC gateway. Submit feedback events as users
interact with items, then query the engine for ranked
recommendations per user.

```python
import requests

base = "{{ SERVICE_BASE_URL }}"
headers = {"Authorization": "Bearer {{ API_KEY }}"}

# Tell the engine a user liked an item.
requests.post(f"{base}/api/feedback", headers=headers, json=[
    {"UserId": "{{ USER_ID }}", "ItemId": "item-42", "FeedbackType": "like"},
])

# Ask for that user's top-5 recommendations.
resp = requests.get(
    f"{base}/api/recommend/{{ USER_ID }}",
    headers=headers,
    params={"n": 5},
)
print(resp.json())
```

The gateway authenticates you against your UnitySVC API key, scopes
the request to your enrollment's namespace, and forwards to the
upstream Gorse instance.
