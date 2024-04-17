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

            if not session_key:
                request.session.save()
                session_key = request.session.session_key
                print("not ##################333", session_key)

            print("session-key", session_key)
            previous_questions = request.session.get('previous_questions', [])
            print(previous_questions) 
            # user's question
            prompt = request.data['question']
            previous_questions.append(prompt)

            chat_history = [{'role' : 'system', 'content' : 'You are a crypto assisstant and you only answer questions realted to crypto , nothing else.'}]

            for question in previous_questions :
                chat_history.append({'role' : 'user', 'content' : question})

            # setup for the system
            # setup = request.data['setup']

            # open ai chat response
            response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=chat_history,
                        max_tokens=100,
                        temperature=0.7,
                        )
           
            content = response.choices[0].message.content
            request.session['previous_questions'] = previous_questions
            return Response({'answer' : content}, status=200)

        except Exception as e:
            print("chat bot error: ", str(e))
            return Response({"error": "Something went wrong while generating the response."}, status=400)