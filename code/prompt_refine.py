# the goal is to let LLMs understand AND, OR relationships

# prepare for a context for OR
context_for_or = """
Role:
You are a professional app engineer, understanding event reporting logics behind app behavior very well.

Context:
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "200"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "201"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "502"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "504"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "204"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "500"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "304"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "429"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "400"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "524"}
{"event_name": "network_request", "attribute_name": "user_logged_in", "attribute_value": "true"}

Each line of the above content represents an attribute of an event and a possbile values it can hold.
Each line has 3 fields: "event_name", "attribute_name" and "attribute_value". 
- "event_name" gives you the name of an event.
- "attribute_name" gives you the name of the attribute for an event.
- "attribute_value" gives you one possible value for an attribute.
An event can have multiple attributes, and an attribute can have multiple values.

Tasks:
Understand the given context and complete the following tasks:
Step 0
In the given context, choose those lines that relate to the app behavior: success network request
Step 1
Based on your chosen lines, come out a mapping rule for the app behavior: success network request
Step 2
Based on the mapping rule you produced, come out a confidence value that represents to which extent you think we can trust it.
Step 3
In the end, output a JSON in your response that contains the confidence value and the mapping rule.
"""

# # # # # # # # # # 

# prepare for a context for AND
context_for_and = """
Role:
You are a professional app engineer, understanding event reporting logics behind app behavior very well.

Context:
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "200"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "201"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "502"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "504"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "204"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "500"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "304"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "429"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "400"}
{"event_name": "network_request", "attribute_name": "status_code", "attribute_value": "524"}
{"event_name": "network_request", "attribute_name": "user_logged_in", "attribute_value": "true"}

Each line of the above content represents an attribute of an event and a possbile values it can hold.
Each line has 3 fields: "event_name", "attribute_name" and "attribute_value". 
- "event_name" gives you the name of an event.
- "attribute_name" gives you the name of the attribute for an event.
- "attribute_value" gives you one possible value for an attribute.
An event can have multiple attributes, and an attribute can have multiple values.

Tasks:
Understand the given context and complete the following tasks:
Step 0
In the given context, choose those lines that relate to the app behavior: login network request and 400 response code
Step 1
Based on your chosen lines, come out a mapping rule for the app behavior: login network request and 400 response code
Step 2
Based on the mapping rule you produced, come out a confidence value that represents to which extent you think we can trust it.
Step 3
In the end, output a JSON in your response that contains the confidence value and the mapping rule.
"""

# prepare for a format instruction to LLM outputs
format_instruction = """
The output should conform to the below JSON schema:
{
    "$defs": {
        "SingleEventAttributeNameFilter": {
            "description": "an event can be filtered by one or more mapping rules using the below properties",
            "properties": {
                "attribute_name": {
                    "description": "gives you the name of the attribute for an event",
                    "example": "series_title",
                    "title": "Attribute Name",
                    "type": "string"
                },
                "op": {
                    "description": "the comparison operators you can apply. valid operators include 'eq': equals; 'not eq': not equals; 'contains': contains; 'not contains': does not contain",
                    "enum": [
                        "eq",
                        "not eq",
                        "contains",
                        "not contains"
                    ],
                    "example": "eq",
                    "title": "Op",
                    "type": "string"
                },
                "attribute_value": {
                    "description": "gives you one possible value for an attribute",
                    "example": "football",
                    "title": "Attribute Value",
                    "type": "string"
                }
            },
            "required": [
                "attribute_name",
                "op",
                "attribute_value"
            ],
            "title": "SingleEventAttributeNameFilter",
            "type": "object"
        },
        "SingleEventRule": {
            "description": "an event rule is a set of mapping rules for an event",
            "properties": {
                "mapping_rules": {
                    "anyOf": [
                        {
                            "items": {
                                "items": {
                                    "$ref": "#/$defs/SingleEventAttributeNameFilter"
                                },
                                "type": "array"
                            },
                            "type": "array"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "description": "an event may contains multiple mapping rules. if there is no mapping rule for an event, that means you want all of attributes for that event. if you generate multiple mapping rules, use the first-level array ([]) to represent the logical AND between mapping rules, use the second-level array ({}) to represent the logical OR between mapping rules"
                    "example for logical AND between mapping rules": [
                        [
                            {
                                "attribute_name": "player_name",
                                "attribute_value": "AndroidTV",
                                "op": "not eq"
                            }
                        ],
                        [
                            {
                                "attribute_name": "player_name",
                                "attribute_value": "FireTV",
                                "op": "not eq"
                            }
                        ]
                    ],
                    "example for logical OR between mapping rules": [
                        [
                            {
                                "attribute_name": "player_name",
                                "attribute_value": "AndroidTV",
                                "op": "eq"
                            },
                            {
                                "attribute_name": "player_name",
                                "attribute_value": "FireTV",
                                "op": "eq"
                            }
                        ]
                    ],
                    "title": "Mapping Rules"
                },
                "event_name": {
                    "description": "gives you the name of an event to which mapping rules apply",
                    "example": "conviva_application_background",
                    "title": "Event Name",
                    "type": "string"
                }
            },
            "required": [
                "mapping_rules",
                "event_name"
            ],
            "title": "SingleEventRule",
            "type": "object"
        }
    },
    "description": "represents the overall filtering criteria where the collection evaluates to true only if all the event rules are satisfied",
    "properties": {
        "confidence_level": {
            "description": "represents to which extent you think we can trust the event rules",
            "example": 50,
            "maximum": 100,
            "minimum": 0,
            "title": "Confidence Level",
            "type": "integer"
        },
        "event_rules": {
            "description": "an event rule is a set of mapping rules for an event",
            "example": [
                {
                    "event_name": "open_replay",
                    "mapping_rules": [
                        [
                            {
                                "attribute_name": "series_title",
                                "attribute_value": "football",
                                "op": "contains"
                            }
                        ],
                        [
                            {
                                "attribute_name": "user_id",
                                "attribute_value": "739986",
                                "op": "not eq"
                            }
                        ]
                    ]
                },
                {
                    "event_name": "conviva_application_background",
                    "mapping_rules": [
                        [
                            {
                                "attribute_name": "player_name",
                                "attribute_value": "AndroidTV",
                                "op": "eq"
                            },
                            {
                                "attribute_name": "player_name",
                                "attribute_value": "FireTV",
                                "op": "eq"
                            }
                        ]
                    ]
                },

            ],
            "items": {
                "$ref": "#/$defs/SingleEventRule"
            },
            "title": "Event Rules",
            "type": "array"
        }
    },
    "required": [
        "confidence_level",
        "event_rules"
    ]
}

As an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}
The object {"foo": ["bar", "baz"]} is a well-formatted Json schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted Json schema.
"""

# set up prompts for AND, OR
prompt_for_or = context_for_or + format_instruction
prompt_for_and = context_for_and + format_instruction
# print(prompt_for_and)

# request event mapping rules from API
import requests

url = "https://.../inference"

# request body
payload = {
    "prompt": prompt_for_or   # success request network
    "prompt": prompt_for_and  # login request network and 400 response code
}

# request header
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers) # use http POST method
    
# check request status
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("request error code:", response.status_code)
