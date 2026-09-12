# MapQuest Route Directions

A simple Flask web application that uses the MapQuest Directions API to calculate driving directions between two locations.

The application accepts an origin and destination, sends the information to the MapQuest API, and displays the estimated travel duration, distance, and step-by-step driving maneuvers.

## Features

- Enter a starting location
- Enter a destination
- Get route directions using the MapQuest Directions API
- Display estimated trip duration
- Display total distance in kilometers
- Display step-by-step driving maneuvers
- Error handling for invalid requests and API problems
- Simple web-based interface using Flask

## Technologies Used

- Python
- Flask
- Requests
- HTML
- CSS
- MapQuest Directions API

## Project Structure

```text
MapQuest/
│
├── .venv/
│
├── templates/
│   └── index.html
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── mapquest_parse-json1.py
├── mapquest_parse-json2.py
├── mapquest_parse-json3.py
├── mapquest_parse-json4.py
├── mapquest_parse-json5.py
├── mapquest_parse-json6.py
└── mapquest_parse-json7.py
```
## Installation

1. Clone the repo

```bash
git clone https://github.com/codeyson/MapQuest.git
```
2. Create a virtual environment

```bash
python -m venv .venv
```

3. Activate the Virtual Environment
```bash
.venv\Scripts\actvitate
```

4. Install Dependencies
```bash
python -m pip install -r requirements.txt
```