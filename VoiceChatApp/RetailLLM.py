from retell import Retell
from retell.resources.llm import LlmResponse
from retell.resources.agent import AgentResponse
from retell.resources.phone_number import PhoneNumberResponse
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env.


retell_client = Retell(
        api_key=os.environ.get('API_KEY')
    )


def retellAPI(request):
    protocol = 'https'
    base_url = f"{protocol}://{request.get_host()}"
    llm: LlmResponse = retell_client.llm.create(
        general_prompt="You are a friendly agent that helps people understand Web3 technology and cryptocurrencies.",
        begin_message= "Hey, I'm your virtual Web3 and cryptocurrencies assistant, how can I help you?",
        general_tools= [
            {
                "type": "end_call",
                "name": "end_call",
                "description":
                    "End the call with user only when user said bye and thanks",
            },
            {
                "type": "custom",
                "name": "book_google_calendar_event",
                "description":
                    "Book an event on Google Calendar when a user provides their name, email, and selects a time for scheduling an appointment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the user for whom the event is being booked."
                        },
                        "start_time": {
                            "type": "string",
                            "description": "The start time of the event in ISO 8601 format."
                        },
                         "email": {
                            "type": "string",
                            "description": "The email of the user for whom the event is being booked."
                        }
                    },
                    "required": ["name", "time", "email"],
                },
                "speak_during_execution": True,
                "speak_after_execution": True,
                "url": base_url + "/create_event?name={name}&start_time={start_time}&email={email}",
            },
        ],
    )
    print(llm)

    # Create an agent and assign LLM address
    agent: AgentResponse = retell_client.agent.create(
    llm_websocket_url=llm.llm_websocket_url,
    voice_id="11labs-Adrian",
    agent_name="Ryan"
    )
    print(agent)
    return agent


def get_retell_phoneNumber(agent):
    # Purhcase a phone number
    phone: PhoneNumberResponse = retell_client.phone_number.create(
    agent_id=agent.agent_id,
    )
    print(phone)
    return phone