import time
from tools import tools
from google.cloud import bigquery
import streamlit as st
import time
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool
import requests
import re

st.set_page_config(
    page_title="API Flow Weaver",
    page_icon=":bar_chart:",
    layout="wide",
)


model = GenerativeModel(
    "gemini-1.0-pro",
    generation_config={"temperature": 0},
    tools=tools(),
    )


col1, col2 = st.columns([7, 1])
with col1:
    st.title("API Flow Weaver")
with col2:
    st.image("gcp.png", width=200)

st.subheader("Powered by Function Calling in Gemini")


with st.expander("Sample prompts", expanded=True):
    st.write(
        """
        - What is the current weather in New York?
        - What is the current time in London?
        - What is the current weather in London?
        - What is the current time in New York?
    """
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"].replace("$", "\$"))  # noqa: W605
        try:
            with st.expander("Function calls, parameters, and responses"):
                st.markdown(message["backend_details"])
        except KeyError:
            pass

if prompt := st.chat_input("Ask me about information in the database..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        chat = model.start_chat()
        client = bigquery.Client()

        prompt += """
            If the above question does not contain the information you are looking for, ask me again with more details. If it is a weather releated question, and the question does not provide the latitude and longitude, use your rough knowledge of the location to provide the latitude and longitude. For example, the latitude and longitude of New York is 40.7128 and -74.0060 respectively.
        
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
                
                #https://api.weatherbit.io/v2.0/current?lat=35.7796&lon=-78.6382&key=API_KEY&include=minutely

                if response.function_call.name == "get_current_weather":
                    location = params["location"]
                    lat = params["latitude"]
                    lon = params["longitude"]
                    api_key = "API_KEY" # replace with your own API key
                    # api_response = f"The Weather is 40° F in {location}"
                    # api_requests_and_responses.append(
                    #     [response.function_call.name, params, api_response]
                    # )
                    api_response = requests.get(f"https://api.weatherbit.io/v2.0/current?lat={lat}&lon={lon}&key={api_key}&include=minutely")
                    api_response = api_response.json()
                    api_requests_and_responses.append(
                        [response.function_call.name, params, api_response]
                    )

                if response.function_call.name == "get_time":
                    time_zone = params["time_zone"]
                    api_response = requests.get(f"http://worldtimeapi.org/api/timezone/{time_zone}")
                    api_response = api_response.json()["datetime"]
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
                with message_placeholder.container():
                    st.markdown(backend_details)

            except AttributeError:
                function_calling_in_process = False

        time.sleep(3)
        print(response)
        full_response = response.text
        with message_placeholder.container():
            st.markdown(full_response.replace("$", "\$"))  # noqa: W605
            with st.expander("Function calls, parameters, and responses:"):
                st.markdown(backend_details)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": full_response,
                "backend_details": backend_details,
            }
        )