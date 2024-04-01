import vertexai
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerativeModel,
    Part,
    Tool,
)

def tools():
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
    
    get_time_func = FunctionDeclaration(
    name="get_time",
    description="Get the current time",
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
    
    toolset = Tool( 
            function_declarations=[
                get_current_weather_func,
                get_time_func,
            ],
    )

    return [toolset]
    