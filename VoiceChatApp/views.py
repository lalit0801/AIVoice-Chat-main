from rest_framework import generics
from django.shortcuts import render
from .RetailLLM import *
from django.http import HttpResponse, HttpRequest, QueryDict
from rest_framework.request import Request
from .Google import Create_Service
from datetime import datetime,timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import os
from rest_framework.views import APIView
from openai import OpenAI
import json
import requests
from datetime import datetime, timedelta
from django.http import StreamingHttpResponse
import re

# tested
CLIENT_SECRET_FILE = os.path.abspath('new_one.json')

API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Create your views here.


def call(request):
    agent = retellAPI(request)
    phone_number = get_retell_phoneNumber(agent)
    return HttpResponse("Model run successfully")

def index_view(request):
    return render(request, 'index.html')


class CreateEvent(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data.get('args')
        service = Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)
        print("yes", data)

        #----------Creating Calendar----------------#

        request_body = {
            'summary': f"{request.data.get('name')}",
            'timeZone': 'Asia/Kolkata'
        }
        response = service.calendars().insert(body=request_body).execute()
        calendar_id = response['id']

        start_time_str = data.get('start_time')
        start_time = datetime.fromisoformat(start_time_str)
        end_time = start_time + timedelta(hours = 1)
        timeZone = 'Asia/Kolkata'
        #----------request body of event-----------#


        event_request_body = {
            'start':{
                'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone' : timeZone,
            },

            'end':{
                'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone' : timeZone
            },

            'summary': f'{request.data.get("name")}',
            'description':'',
            'colorId': 5,
            'Status': 'confirmed',
            'transparency':'opaque',
            'visibility':'private',
            'location':'',
            'attendees':[
                {
                    'displayName' : f'{data.get("name")}',
                    #'comment' : 'cool guy',
                    # 'email' : f'{data.get("email")}',
                    'email':'nitish@snakescript.com',
                    'optional': False,
                    'organizer': True,
                    'responseStatus': 'accepted'
                }
            ]

        }

        maxAttendees = 5
        sendNotification = True
        sendUpdates = 'none'

        #-----------Creating Event------------#

        response = service.events().insert(calendarId = calendar_id,maxAttendees =maxAttendees,sendNotifications=sendNotification,sendUpdates=sendUpdates,body=event_request_body,).execute()

        print(response, "---------")

        return Response({"message":"booked successfully"}, status=status.HTTP_200_OK)

class ChatBotView(generics.CreateAPIView):
    
    def post(self, request,*args, **kwargs):
        print(request,"===request==")
        print(request.data)
        user_message= request.data
      
        # create event function
        def create_event(content):
            print(content)
            # content= 
            # if "Success" in content:
                # Extracting JSON content from the response
            json_match = re.search(r'``` json\s*(\{.*\})\s*```', content)
            if json_match:
                json_string = json_match.group(1)
                print(json_string)
                # Convert the JSON string to a dictionary
                json_data = eval(json_string)  # Note: Use ast.literal_eval for security
                # Remove whitespaces from keys
                json_data = {key.strip(): value for key, value in json_data.items()}
                print(json_data)
                print(type(json_data))
                print(json_data['title'])
                print(json_data['length of event'])# Accessing the key without whitespaces
    

                    # Calling create_event API based on content received
                print("******")
                
                # Establish a connection to the server

                cal_api_key= os.getenv('CAL_API_KEY')
                reqUrl = f"https://api.cal.com/v1/event-types?apiKey={cal_api_key}"

                headersList = {
                "Content-Type": "application/json" ,
                }

                payload = json.dumps(
                {
                    "title": json_data.get('title', ''),
                    "slug": json_data.get('title', '').lower().replace(' ', '-'),
                    "length": int(json_data.get('length of event', '10')),
                    "metadata":{}
                })

                response = requests.request("POST", reqUrl, data=payload,  headers=headersList)

                print(response.text)
                response_object = json.loads(response.text)
                
                # start_time= json_data['start_time']
                # Extract the ID from the event_type object
                event_type_id = response_object['event_type']['id']
                
                
                print(event_type_id)
                start_time= "2024-04-30 04:00 PM IST"
                
                print(start_time)
                print(type(start_time))
                booking(event_type_id, start_time)
                if response.status_code == 200:
                    # Return success response
                    print("successfully created event")
                else:
                    # Return error response
                    print("failed to create event")
        
        
        def booking(event_id, start_time):
            # cal_api_key= os.getenv('CAL_API_KEY')
            reqUrl = "https://api.cal.com/v1/bookings?apiKey=cal_live_8e81f4c669a52ae5494c746e188e4f4a"
            
            print('11')

            headersList = {
            "Content-Type": "application/json" 
            }

            payload = json.dumps(
            {
            
                "eventTypeId": event_id,
                "start": start_time,
                "end": "2024-04-30 04:10 PM IST",
                "responses": {
                "name": "Lalit Kumar Yadav",
                "email": "lalit@snakescript.com",
                
                },
                "timeZone": "Asia/Kolkata",
                "language": "en",
                "metadata":{}
            
            })
            print('22')
            response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
            print(response.text)
            if response.status_code == 200:
                                    # Return success response
                print("successfully booked")
            else:
                # Return error response
                print("failed to book")

            # print(response.text)
        def generate_response(user_message):  
                api_key= os.getenv( 'OPENAI_API_KEY')
                client = OpenAI(api_key = api_key)
                global concatenated_response  # Declare concatenated_response as global
                concatenated_response = "" 
                # Custom prompting of system and user
                chat_history= [
                    {
                "role": "system",
                "content": f"""
                !IMPORTANT Please follow these steps:
                1. You are Crypto Assistant: It answers all the questions realted to crypto only , nothing else.Strictly,It only answer question other than crypto, if a question for information purpose is asked.
                """
                },
                    {
                        "role": "system",
                        "content": f"""
                        !IMPORTANT Please follow these steps one by one:
                        1. Your purpose is to analyze {user_message}. If you find anything only related to "what services you provide" , respond with "BOOK AN APPOINTMENT. Type: "Confirm My Appointment" TO CONFIRM YOUR APPOINTMENT AND SEE FOR AVAILABLE SLOTS".Otherwise be crypto assistant.
                        2. After first step , analyze {user_message}. If you find the exact words "Confirm My Appointment". Respond with Message "Available Slots will be shown. Enter Details in the same format: title: "your_event_title", length of event: "35".Otherwise be crypto assistant.
                        3. After second step, You  purpose is to  analyze {user_message}. If you find user input in or related format "title: "your_event_title", length of event: "35"" then strictly respond with Message :"Success" along with convert Data in json format having all the information. Otherwise be crypto assistant.
                        4.
                        """
                    },
                    ] +user_message
                response = client.chat.completions.create(
                                model="gpt-4-turbo",
                                messages=chat_history,
                                max_tokens=50,
                                temperature=0.7,
                                stream= True
                                )
                
                print(response, "==response")
            
                for chunk in response:
                    try:
                        chunk_message = chunk.choices[0].delta.content
                        # print(chunk_message,"==content")
                        # create_event(chunk_message)
                        if chunk_message is not None:
                            concatenated_response += ' '.join(chunk_message.split()) + " "
                            # print(chunk_message,"===chunkmesggase")
                        yield chunk_message
                    except Exception as e:
                        print("Error processing response:", e)
                print(concatenated_response, "==concat_reponse")
                trimmed_string = concatenated_response.strip()
                if "Success" in trimmed_string:
                  create_event(trimmed_string)

        return StreamingHttpResponse(generate_response(user_message), content_type='text/event-stream')

# booking function to add event to calender


        
def chatbot(request):
    return render(request, "chatbot.html")
