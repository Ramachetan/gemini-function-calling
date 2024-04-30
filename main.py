import time
import chainlit as cl
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool
from dotenv import load_dotenv
import os
import requests
import time


load_dotenv()

api_key = os.getenv("WEATHER_API_KEY")
google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
google_cx = os.getenv("GOOGLE_CX")

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if username == "admin" and password == "admin":
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None 

@cl.step
async def google_search(query: str):
    response = requests.get(f"https://www.googleapis.com/customsearch/v1?key={google_search_api_key}&cx={google_cx}&q={query}")
    response_json = response.json()
    api_response = f"Query: {query}\nSearch Results:\n"
    if 'items' in response_json:
        for item in response_json['items']:
            title = item.get('title', 'No title available')
            link = item.get('link', 'No link available')
            snippet = item.get('snippet', 'No snippet available')
            print(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n")
            api_response += f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n"
    else:
        print("No search results found.")
    return api_response
    

@cl.step
async def get_current_weather(location: str, lat: float, lon: float):
    response = requests.get(f"https://api.weatherbit.io/v2.0/current?lat={lat}&lon={lon}&key={api_key}&include=minutely")
    response = response.json()
    api_response = "Weather: 72F Humidity: 50% Wind: 5mph"
    return api_response

@cl.step
async def get_current_time(time_zone: str):
    response = requests.get(f"http://worldtimeapi.org/api/timezone/{time_zone}")
    response = response.json()
    print(response)
    api_response = "The current time in " + time_zone + " is " + response["datetime"] + "Today's date is" + response["datetime"]
    return api_response

google_search_func = FunctionDeclaration(
    name="google_search",
    description="Get search results from Google based on a query. Use this tool whenever you don't know the answer to a question or unsure about a topic.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Refined search query to get the most accurate results.",
            },
        },
        "required": ["query"],
    },
)

get_current_weather_func = FunctionDeclaration(
    name="get_current_weather",
    description="Get the current weather in a given location. Use your knowledge of latitude and longitude to get the weather for a location.",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The location to get the weather for. For example, 'New York, NY' or 'London, UK'",
            },
            "latitude": {
                "type": "number",
                "description": "The latitude of the location to get the weather for",
            },
            "longitude": {
                "type": "number",
                "description": "The longitude of the location to get the weather for",
            },
            
        },
        "required": ["location", "latitude", "longitude"],
    },
    
    )

get_current_time_func = FunctionDeclaration(
    name="get_current_time",
    description="Get the current time and date in a given time zone. Use this tool before googling questions that are time sensitive.",
    parameters={
        "type": "object",
        "properties": {
            "time_zone": {
                "type": "string",
                "description": "The time zone to get the time for. For example, 'America/New_York' or 'Europe/London'",
            },
        },
        "required": ["time_zone"],
    },
        
    )

sql_query_tool = Tool(
    function_declarations=[
        google_search_func,
        get_current_weather_func,
        get_current_time_func,
    ],
)

model = GenerativeModel(
    "gemini-1.0-pro-001",
    generation_config={"temperature": 0},
    tools=[sql_query_tool],
)

@cl.on_chat_start
async def start():
    await cl.Avatar(
        name="Gemini",
        url="https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg",
    ).send()

@cl.on_message
async def main(message: cl.Message):
    
        full_response = ""
        current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        chat = model.start_chat(response_validation=False)
        
        prompt = "User Question: "+ message.content + "\n"
        
        prompt += f"""
            You are Gemini, a large language model trained by Google. Current date: {current_date}
            
            You have the tool `google search`. Use `google search` in the following circumstances: - User is asking about current events or something that requires real-time information (weather, sports scores, etc.) - User is asking about some term you are totally unfamiliar with (it might be new) - User explicitly asks you to browse the web for information. Note: The more specific the query, the more accurate the results. For example, if user asks 'When does Google Next Happen?' the query should be 'Google Next 2024 date'. ALWAYS refine the user question to get the most accurate results, NEVER use the user question as is. If you are unsatisfied with the original results retry with a better query. Think Step by Step: 1. Understand the user question 2. Refine the query 3. Get the search results 4. Summarize the search results in a concise manner.
            """

        response = chat.send_message(prompt)
        response = response.candidates[0].content.parts[0]

        print(response)

        api_requests_and_responses = []
        backend_details = ""

        function_calling_in_process = True
        while function_calling_in_process:
            try:
                params = {}
                for key, value in response.function_call.args.items():
                    params[key] = value

                print(response.function_call.name)
                print(params)

                if response.function_call.name == "get_current_weather":
                    location = params["location"]
                    lat = params["latitude"]
                    lon = params["longitude"]
                    api_response = await get_current_weather(location, lat, lon)
                    api_requests_and_responses.append(
                        [response.function_call.name, params, api_response]
                    )

                if response.function_call.name == "google_search":
                    api_response = await google_search(params["query"])
                    api_requests_and_responses.append(
                        [response.function_call.name, params, api_response]
                    )
                    
                if response.function_call.name == "get_current_time":
                    time_zone = params["time_zone"]
                    api_response = await get_current_time(time_zone)
                    api_requests_and_responses.append(
                        [response.function_call.name, params, api_response]
                    )
                

                print(api_response)

                response = chat.send_message(
                    Part.from_function_response(
                        name=response.function_call.name,
                        response={
                            "content": api_response,
                        },
                    ),
                )
                response = response.candidates[0].content.parts[0]

                backend_details += "- Function call:\n"
                backend_details += (
                    "   - Function name: ```"
                    + str(api_requests_and_responses[-1][0])
                    + "```"
                )
                backend_details += "\n\n"
                backend_details += (
                    "   - Function parameters: ```"
                    + str(api_requests_and_responses[-1][1])
                    + "```"
                )
                backend_details += "\n\n"
                backend_details += (
                    "   - API response: ```"
                    + str(api_requests_and_responses[-1][2])
                    + "```"
                )
                backend_details += "\n\n"
                # with message_placeholder.container():
                #     st.markdown(backend_details)

            except AttributeError:
                function_calling_in_process = False

        time.sleep(3)
        text_content = backend_details
        # elements = [
        #     cl.Text(name="Function Call Process", content=text_content, display="inline")
        # ]

        full_response = response.text
        await cl.Message(
            content=full_response,
            author="Gemini",
        ).send()
        
        
