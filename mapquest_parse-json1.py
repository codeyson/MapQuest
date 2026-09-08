import os
import urllib.parse
import requests

main_api = os.getenv("MAIN_API")
orig = "Roma, Italia"
dest = "Frascati, Italia"
key = os.getenv("KEY")

url = main_api + urllib.parse.urlencode({"key":key, "from":orig, "to":dest})

json_data = requests.get(url).json()
print(json_data)
