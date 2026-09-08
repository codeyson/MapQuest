import os
import urllib.parse
import requests

main_api = os.getenv("MAIN_API")
orig = "Washington, D.C."
dest = "Baltimore, Md"
key = os.getenv("KEY")

url = main_api + urllib.parse.urlencode({"key":key, "from":orig, "to":dest})

json_data = requests.get(url).json()
print("URL: " + (url))

json_data = requests.get(url).json()
json_status = json_data["info"]["statuscode"]

if json_status == 0:
    print("API Status: " + str(json_status) + " = A successful route call.\n")
