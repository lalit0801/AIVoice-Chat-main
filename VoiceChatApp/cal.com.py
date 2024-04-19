import requests
import json

# Set the API endpoint and headers
url = "https://api.cal.com/v1/event-types?apiKey=cal_live_0aa50476d76c04be2e1d9b16e961081b"
headers = {
    "Content-Type": "application/json",
   
}

# Set the request body
data = {
  "summary": "An example of an individual event type POST request",
  "value": {
    "title": "Hello World",
    "slug": "hello-world",
    "length": 30,
    "hidden": False,
    "position": 0,
    "eventName": null,
    "timeZone": null,
    "scheduleId": 5,
    "periodType": "UNLIMITED",
    "periodStartDate": "2023-02-15T08:46:16.000Z",
    "periodEndDate": "2023-0-15T08:46:16.000Z",
    "periodDays": null,
    "periodCountCalendarDays": False,
    "requiresConfirmation": False,
    "recurringEvent": n,
    "disableGuests": false,
    "hideCalendarNotes": false,
    "minimumBookingNotice": 120,
    "beforeEventBuffer": 0,
    "afterEventBuffer": 0,
    "price": 0,
    "currency": "usd",
    "slotInterval": null,
    "successRedirectUrl": null,
    "description": "A test event type",
    "metadata": {
      "apps": {
        "stripe": {
          "price": 0,
          "enabled": false,
          "currency": "usd"
        }
      }
    }
  }
}

# Make the POST request
response = requests.post(url, headers=headers, json=data)

# Check the status code
if response.status_code == 200:
    print("Event created successfully")
    print(response.json())
else:
    print("Error creating event:", response.content)
