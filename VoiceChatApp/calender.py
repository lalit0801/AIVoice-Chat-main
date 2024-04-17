from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .Google import Create_Service
from datetime import datetime, timedelta

CLIENT_SECRET_FILE = '/Users/mac/Desktop/Ai Voice and chat 2/new_one.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Initialize Google Calendar service
service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

@csrf_exempt
def create_event(request):
    data = request.POST
    summary = data.get('summary', 'Event Summary')
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=2)
    timeZone = 'Asia/Kolkata'

    event_request_body = {
    'start':{
        'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone' : timeZone,
    },

    'end':{
        'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone' : timeZone
    },

    'summary': 'MLProj Meet',
    'description':'Discussion of the final yr project',
    'colorId': 5,
    'Status': 'confirmed',
    'transparency':'opaque',
    'visibility':'private',
    'location':'Thane, Viviana',
    'attendees':[
        {
            'displayName' : 'Tom',
            'comment' : 'cool guy',
            'email' : 'tp@example.com',
            'optional': False, #optional: means whether this attendee is optional or not
            'organizer': True,
            'responseStatus': 'accepted'
        }
    ]

}
    # Insert event
    response = service.events().insert(calendarId='primary', body=event_request_body).execute()

    return JsonResponse(response)
