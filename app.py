import os
import urllib.parse
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

main_api = os.getenv("MAIN_API")
key = os.getenv("KEY")


def get_transport_info(maneuver, route_has_ferry=False):
    """
    Determine the transportation type for an individual maneuver.

    MapQuest may return AUTO for driving maneuvers even when the
    overall route contains a ferry. Therefore, ferry detection also
    checks the maneuver attributes and narrative.
    """

    transport_mode = maneuver.get("transportMode", "AUTO")
    attributes = maneuver.get("attributes", 0)
    narrative = maneuver.get("narrative", "").lower()

    # Ferry detection
    ferry_words = [
        "ferry",
        "ferry terminal",
        "ferry port",
        "ferry crossing",
        "board ferry",
        "take ferry",
        "onto ferry",
        "ferry boat",
        "boat",
        "ship"
    ]

    # MapQuest ferry attribute
    ferry_attribute = False

    try:
        ferry_attribute = bool(int(attributes) & 16)
    except (ValueError, TypeError):
        ferry_attribute = False

    if ferry_attribute or (
        route_has_ferry
        and any(word in narrative for word in ferry_words)
    ):
        return {
            "mode": "Ferry",
            "icon": "⛴️",
            "description": "Ferry"
        }

    # Other transport modes
    if transport_mode == "WALKING":
        return {
            "mode": "Walking",
            "icon": "🚶",
            "description": "Walking"
        }

    if transport_mode == "BICYCLE":
        return {
            "mode": "Bicycle",
            "icon": "🚲",
            "description": "Bicycle"
        }

    if transport_mode == "TRUCK":
        return {
            "mode": "Truck",
            "icon": "🚚",
            "description": "Truck"
        }

    # Default MapQuest AUTO
    return {
        "mode": "Car",
        "icon": "🚗",
        "description": "Car"
    }


@app.route("/", methods=["GET", "POST"])
def index():

    result = None
    error = None
    status_message = None

    if request.method == "POST":

        orig = request.form.get("origin", "").strip()
        dest = request.form.get("destination", "").strip()

        if not orig or not dest:

            error = (
                "Please provide both a starting location "
                "and a destination."
            )

        elif orig.lower() == dest.lower():
            error = (
                "The starting location and destination "
                "cannot be the same."
            )

        elif not main_api or not key:

            error = (
                "MAIN_API or KEY environment variable "
                "is missing."
            )

        else:

            try:

                params = {
                    "key": key,
                    "from": orig,
                    "to": dest
                }

                url = (
                    main_api
                    + urllib.parse.urlencode(params)
                )

                response = requests.get(
                    url,
                    timeout=10
                )

                response.raise_for_status()

                json_data = response.json()

                json_status = json_data[
                    "info"
                ]["statuscode"]

                if json_status == 0:

                    route = json_data["route"]
                    leg = route["legs"][0]

                    # --------------------------------
                    # ROUTE FEATURES
                    # --------------------------------

                    features = {

                        "toll": route.get(
                            "hasTollRoad",
                            False
                        ),

                        "highway": route.get(
                            "hasHighway",
                            False
                        ),

                        "bridge": route.get(
                            "hasBridge",
                            False
                        ),

                        "unpaved": route.get(
                            "hasUnpaved",
                            False
                        ),

                        "tunnel": route.get(
                            "hasTunnel",
                            False
                        ),

                        "ferry": route.get(
                            "hasFerry",
                            False
                        ),

                        "country_cross": route.get(
                            "hasCountryCross",
                            False
                        ),

                        "seasonal_closure": route.get(
                            "hasSeasonalClosure",
                            False
                        ),

                        "timed_restriction": route.get(
                            "hasTimedRestriction",
                            False
                        ),

                        "u_turn": route.get(
                            "hasUTurn",
                            False
                        ),

                        "difficult_turn": route.get(
                            "hasDifficultTurn",
                            False
                        )
                    }

                    # --------------------------------
                    # OVERALL TRAVEL METHOD
                    # --------------------------------

                    if features["ferry"]:

                        travel_method = "Land + Ferry"

                        travel_description = (
                            "This route includes land travel "
                            "and a ferry crossing."
                        )

                        travel_icons = "🚗  →  ⛴️  →  🚗"

                    else:

                        travel_method = "Land Travel"

                        travel_description = (
                            "This route can be completed "
                            "by land."
                        )

                        travel_icons = "🚗"

                    # --------------------------------
                    # ROUTE FEATURES
                    # --------------------------------

                    feature_list = []

                    if features["highway"]:
                        feature_list.append({
                            "icon": "🛣️",
                            "name": "Highway"
                        })

                    if features["ferry"]:
                        feature_list.append({
                            "icon": "⛴️",
                            "name": "Ferry"
                        })

                    if features["toll"]:
                        feature_list.append({
                            "icon": "💰",
                            "name": "Toll Road"
                        })

                    if features["bridge"]:
                        feature_list.append({
                            "icon": "🌉",
                            "name": "Bridge"
                        })

                    if features["tunnel"]:
                        feature_list.append({
                            "icon": "🚇",
                            "name": "Tunnel"
                        })

                    if features["unpaved"]:
                        feature_list.append({
                            "icon": "🛤️",
                            "name": "Unpaved Road"
                        })

                    if features["country_cross"]:
                        feature_list.append({
                            "icon": "🌎",
                            "name": "Country Crossing"
                        })

                    if features["seasonal_closure"]:
                        feature_list.append({
                            "icon": "⚠️",
                            "name": "Seasonal Closure"
                        })

                    if features["timed_restriction"]:
                        feature_list.append({
                            "icon": "⏰",
                            "name": "Time Restriction"
                        })

                    if features["difficult_turn"]:
                        feature_list.append({
                            "icon": "⚠️",
                            "name": "Difficult Turn"
                        })

                    # --------------------------------
                    # STEP-BY-STEP DIRECTIONS
                    # --------------------------------

                    maneuvers = []

                    for number, each in enumerate(
                        leg.get("maneuvers", []),
                        start=1
                    ):

                        transport = get_transport_info(
                            each,
                            features["ferry"]
                        )

                        maneuvers.append({

                            "number": number,

                            "narrative": each.get(
                                "narrative",
                                "Continue along the route."
                            ),

                            "distance_km": round(
                                each.get(
                                    "distance",
                                    0
                                ) * 1.60934,
                                2
                            ),

                            "transport_mode":
                                transport["mode"],

                            "transport_icon":
                                transport["icon"],

                            "transport_description":
                                transport["description"]
                        })

                    # --------------------------------
                    # FINAL RESULT
                    # --------------------------------

                    result = {

                        "origin": orig.title(),

                        "destination": dest.title(),

                        "duration": route.get(
                            "formattedTime",
                            "N/A"
                        ),

                        "distance_km": round(
                            route.get(
                                "distance",
                                0
                            ) * 1.60934,
                            2
                        ),

                        "travel_method":
                            travel_method,

                        "travel_description":
                            travel_description,

                        "travel_icons":
                            travel_icons,

                        "features":
                            features,

                        "feature_list":
                            feature_list,

                        "maneuvers":
                            maneuvers
                    }

                    status_message = (
                        "Route successfully retrieved."
                    )

                elif json_status == 402:

                    error = (
                        "Invalid location. Please check "
                        "the starting location and "
                        "destination."
                    )

                elif json_status == 611:

                    error = (
                        "A starting location or "
                        "destination is missing."
                    )

                else:

                    error = (
                        f"MapQuest returned status code "
                        f"{json_status}."
                    )

            except requests.exceptions.Timeout:

                error = (
                    "The MapQuest request took too long. "
                    "Please try again."
                )

            except requests.exceptions.RequestException:

                error = (
                    "Unable to connect to MapQuest. "
                    "Please check your internet connection "
                    "and try again."
                )

            except Exception as e:

                error = (
                    "An unexpected error occurred: "
                    f"{str(e)}"
                )

    return render_template(
        "index.html",
        result=result,
        error=error,
        status_message=status_message
    )


if __name__ == "__main__":
    app.run(debug=True)