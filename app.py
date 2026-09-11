import os
import urllib.parse
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

main_api = os.getenv("MAIN_API")
key = os.getenv("KEY")


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    status_message = None

    if request.method == "POST":
        orig = request.form.get("origin", "").strip()
        dest = request.form.get("destination", "").strip()

        if not orig or not dest:
            error = "Please provide both origin and destination."

        elif not main_api or not key:
            error = "MAIN_API or KEY environment variable is missing."

        else:
            try:
                params = {
                    "key": key,
                    "from": orig,
                    "to": dest
                }

                url = main_api + urllib.parse.urlencode(params)

                response = requests.get(url, timeout=10)
                response.raise_for_status()

                json_data = response.json()
                json_status = json_data["info"]["statuscode"]

                if json_status == 0:
                    route = json_data["route"]["legs"][0]

                    result = {
                        "origin": orig,
                        "destination": dest,
                        "duration": json_data["route"]["formattedTime"],
                        "distance_km": round(
                            json_data["route"]["distance"] * 1.61, 2
                        ),
                        "maneuvers": [
                            {
                                "narrative": each["narrative"],
                                "distance_km": round(
                                    each["distance"] * 1.61, 2
                                ),
                            }
                            for each in route["maneuvers"]
                        ],
                    }

                    status_message = (
                        f"API Status: {json_status} = "
                        "A successful route call."
                    )

                elif json_status == 402:
                    error = (
                        f"Status Code: {json_status}; "
                        "Invalid user inputs for one or both locations."
                    )

                elif json_status == 611:
                    error = (
                        f"Status Code: {json_status}; "
                        "Missing an entry for one or both locations."
                    )

                else:
                    error = (
                        f"For Status Code: {json_status}; "
                        "Refer to the MapQuest API status codes."
                    )

            except requests.exceptions.RequestException as e:
                error = f"Request error: {str(e)}"

            except Exception as e:
                error = f"Error: {str(e)}"

    return render_template(
        "index.html",
        result=result,
        error=error,
        status_message=status_message
    )


if __name__ == "__main__":
    app.run(debug=True)