import requests

# අර කවදාවත් Expire වෙන්නේ නැති දිග ටෝකන් එක මෙතන දාන්න
TOKEN = "EAAZCIWCSFNhQBSNP9mZAKZAgdp62SUvxsTTu7yj1hqZADfGC6a63mqkhnGFizZBxLlUraZAooCVJZCK08OeCUZC9zANZC4WdKTLCSQlaEHawX26eZBfNFkqpiIGAumrfjIvWwZAM3OkgUZAjPxXLdfuW4pUjqpWoWMZAgY2crut4y1GVpmzt3WqZBqv9kdjNOT2xzFTAZDZD"

url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={TOKEN}"
response = requests.get(url)
data = response.json()

print("\n=== ඔයාගේ Page විස්තර ===")
if 'data' in data and len(data['data']) > 0:
    for page in data['data']:
        print(f"පේජ් එකේ නම: {page.get('name')}")
        print(f"නියම Page ID එක: {page.get('id')}")
        print(f"නියම Page Access Token එක: {page.get('access_token')}\n")
else:
    print("දෝෂයක්! නැත්නම් මේ ටෝකන් එකට පේජ් එකක් සම්බන්ධ වෙලා නෑ.")