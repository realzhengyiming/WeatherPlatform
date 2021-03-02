import requests

url = "https://aqicn.org/city/shenzhen/"

response = requests.get(url,timeout=15)
print(response.text)