from rest_framework import generics
from django.shortcuts import render
from .RetailLLM import *
from django.http import HttpResponse
from .Google import Create_Service
from datetime import datetime,timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from openai import OpenAI


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
    
    def post(self, request):
    
        try : 
            # open ai client creation
            api_key= os.getenv( 'OPENAI_API_KEY')
            client = OpenAI(api_key = api_key)
            print("********************************************")
            session_key = request.session.session_key


            # Session Creation
            if not session_key:
                request.session.save()
                session_key = request.session.session_key
                print("not ##################333", session_key)
            print("session-key", session_key)
            
            
            # Initialized list which appends the questions asked for a session
            previous_questions = request.session.get('previous_questions', [])
            print(previous_questions)
            # Appending user's question questions list
            prompt = request.data['question']
            previous_questions.append(prompt)

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
                    1. Your purpose is to analyze {previous_questions}. If you find anything only related to "what services you provide" , respond with "BOOK AN APPOINTMENT. Type: "Confirm My Appointment" TO CONFIRM YOUR APPOINTMENT AND SEE FOR AVAILABLE SLOTS".Otherwise be crypto assistant.
                    2. After first step , analyze {previous_questions}. If you find the exact words "Confirm My Appointment". Respond with Message "Available Slots will be shown. Enter Details in the same format: name: "your_name", start_time:"12:45 PM"".Otherwise be crypto assistant.
                    3. After second step, You  purpose is to  analyze {previous_questions}. If you find user input in or related format "name: "your_name", start_time:"12:45 PM"" then respond with Message :"Success" and convert Data in json format having all the information. Otherwise be crypto assistant.
                    4.
                    """
                },
               ]
            for question in previous_questions :
                chat_history.append({'role' : 'user', 'content' : question})

            # setup for the system
            # setup = request.data['setup']

            # if prompt.lower()= "what services you provide"
            # open ai chat response
            response = client.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=chat_history,
                        max_tokens=100,
                        temperature=0.7,
                        )

            content = response.choices[0].message.content
            print(content)
            print(request.path,"path here")
            # Calling create_event API based on content recieved
            if "Success" in content:
                # Extracting JSON content from the response
                json_start_index = content.find('```json\n')
                if json_start_index != -1:
                    json_start_index += len('```json\n')
                    json_end_index = content.find('```', json_start_index)
                    if json_end_index != -1:
                        json_content = content[json_start_index:json_end_index]
                        json_data = json.loads(json_content)
                        print("json converted")
                        print(json_data)

                        # Calling create_event API based on content received
                        print("******")
                        # setting request data

                        create_event = CreateEvent()
                        response = create_event.post(request=request)
                        print(response.data,"response_data")

            
            
            request.session['previous_questions'] = previous_questions
            return Response({'answer' : content}, status=200)

        except Exception as e:
            print("chat bot error: ", str(e))
            return Response({"error": "Something went wrong while generating the response."}, status=400)
