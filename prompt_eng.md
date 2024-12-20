### Instructions for Prompt Engineering

#### 1. Be Clear and Specific

Clarity and specificity are essential for getting accurate and relevant responses.

- "Give me a brief overview of deep learning."

#### 2. Define the Structure or Format

Specify if you want the response in a particular format, like a list, comparison, or bullet points.

- "Summarize the benefits of deep learning in bullet points."

#### 3. Set a Role or Context

Assign the model a role to get responses in a specific tone or from a particular perspective.

- "You are a travel guide. Suggest an itinerary for a 3-day trip to Tokyo."

#### 4. Ask for Examples

Request examples to clarify abstract concepts or complicated ideas.

- "Explain the concept of deep learning with a real-world example."

#### 5. Define Constraints or Limitations

Limiting the scope can lead to more concise and relevant responses.

- "Describe the benefits of deep learning in under 100 words."

#### 6. Request Step-by-Step Instructions

For processes, guides, or explanations, ask for a step-by-step breakdown.

- "Explain how to step up a deep learning project in Python step by step."

#### 7. Prompt for Research or Citations

Ask the LLM to back up its claims with references or details.

- "What are the current theories on deep learning? Provide sources if possible."


### Example: Predict Rules Based on Given Context 

```
Role:
You are a professional app engineer, understanding event reporting logics behind app behavior very well.

Context:
{context}
Each line of the above content represents an attribute of an event and a possbile values it can hold.
Each line has 3 fields: "event_name", "attribute_name" and "attribute_value". 
- "event_name" gives you the name of the event.
- "attribute_name" gives you the name of the attribute for the event.
- "attribute_value" gives you one possible value for the attribute.
An event can have multiple attributes, and an attribute can have multiple values.

Tasks:
Understand the above context and complete the following tasks:
Step 1
First, come out a mapping rule for the app behavior: 
{event_description}
Step 2
Based on the mapping rule you produced, come out a confidence value that represents to which extent you think we can trust this mapping rule.
Step 3
In the end, output a JSON in your response that contains the confidence value and the mapping rule, based on the below format:
{format_instructions}
```
