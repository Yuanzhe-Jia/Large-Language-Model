# step 1
# get ground truth data

from clickhouse_connect import get_client
import pandas as pd
import ast

# set up a client
client = get_client(host='localhost', port='8123', username='default', password='', database='default')

# define sql query
sql = """
select distinct on (1)
    lower(event_name) as event_name,
    event_metadata
from default.
where 
    save_date=today() 
    and is_latest=1 
    and mapping_rule <> '{}' 
"""

# save the result to a dataframe
df_data = client.query_df(sql)

# convert original data type (str) to (dict)
df_data['event_metadata'] = [ast.literal_eval(i) for i in df_data['event_metadata']]

# llm is too expensive!!! let's sampling
df_data = df_data.sample(n=20)

# show result
# print("sample data:", "\n", df_data.head(3))
# print()
# print("data size:", df_data.shape[0])



# step 2
# get predicted data

import requests

# request url
url = "https://.../event-rules"

# request header
headers = {"Content-Type": "application/json"}

# change different sources and models when you validate different prompt templates
# prompt version
source = "yuanzhe_v2"
# llm model
model = "gemini-1.5-pro"

# lists to save predicted data
pred_confidence_levels = []
pred_rules = []

# define a loop to retrive the predicted confidence level and mapping rule for each mapped event
for i in df_data['event_name']:

    payload = {
        "mapped_event_name": i,
        "source": source,
        "model": model
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    # check request status
    if response.status_code == 200:
        data = response.json()

        #print(i)
        #print(data['confidence_level'])
        #print(data['rules'])
        #print()

        pred_confidence_levels.append(data['confidence_level'])
        pred_rules.append(data['rules'])

#
# check if the number of predicted data == the number of ground truth data?
# len(pred_confidence_levels) == df_data.shape[0]



# step 3

# convert predicted mapping rules to predicted event metadata

pred_event_metadata = []

for event_group in pred_rules[:idx]:
    event_names = []
    tag_keys = []
    tag_values = []

    for event in event_group[0]:
        event_names.append([event['op'], event['value'][0]])
        if event['mapping_rules']:
            tag_keys.append([event['mapping_rules'][0][0]['tag_key']['op'], event['mapping_rules'][0][0]['tag_key']['value'][0]])
            tag_values.append([event['mapping_rules'][0][0]['tag_value']['op'], event['mapping_rules'][0][0]['tag_value']['value'][0]])
        else:
            tag_keys.append([])
            tag_values.append([])

    pred_event_metadata.append({
        "event_name": event_names,
        "tag_key": tag_keys,
        "tag_value": tag_values
    })

# len(pred_event_metadata)

# extract predicted raw event names from predicted event metadata

pred_raw_event_names = []
for i in pred_event_metadata:

    event_list = []
    for j in i['event_name']:
        event_list.append(j[1])

    pred_raw_event_names.append(event_list)

# len(pred_raw_event_names)

# extract raw event names from event metadata

raw_event_names = []
for i in df_data['event_metadata']:

    event_list = []
    for j in i['event_name']:
        event_list.append(j[1])

    raw_event_names.append(event_list)

# len(raw_event_names)

# combine predicted data and ground truth data

df_data['raw_event_name'] = raw_event_names
df_data['pred_event_rule'] = pred_rules
df_data['pred_event_metadata'] = pred_event_metadata
df_data['pred_raw_event_name'] = pred_raw_event_names
df_data['pred_confidence_level'] = pred_confidence_levels

# print(df_data.head(3))



# step 4

# get raw event tagkeys

raw_event_tagkeys = []
for i in df_data['event_metadata']:

    tagkey_list = []
    for j in i['tag_key']:
        tagkey_list.append(j[1])

    raw_event_tagkeys.append(tagkey_list)

# get retrieved event tagkeys from api

import requests

# request url
url = "https://.../retriever"

# request header
headers = {"Content-Type": "application/json"}

# lists to save predicted data

retrieved_event = []

# define a loop to retrive the predicted confidence level and mapping rule for each mapped event
for i in df_data['event_name']:

    payload = {
        "query": i
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    # check request status
    if response.status_code == 200:
        data = response.json()
        retrieved_event.append(data)

#
# check if the number of retrieved data == the number of ground truth data?
# len(retrieved_event) == df_data.shape[0]

# extract unique tagkeys from retrieved data

retrieved_event_tagkeys = []
for group in retrieved_event:
    tagkeys = {item['attribute_name'] for item in group}
    retrieved_event_tagkeys.append(list(tagkeys))

#
# check if the number of retrieved data == the number of ground truth data?
# len(retrieved_event_tagkeys) == df_data.shape[0]



# step 5

# output accuracy

print("******          accuracy report          ******")
print()

import numpy as np

print("the accuracy to predict the same raw event names:")
print("{:.2f}%".format(np.average([df_data['raw_event_name'] == df_data['pred_raw_event_name']]) * 100))
print()
print("the accuracy to predict the same mapping rules - raw event names and tagkey/value mapping conditions:")
print("{:.2f}%".format(np.average([df_data['event_metadata'] == df_data['pred_event_metadata']]) * 100))
print()
print("the precentage that ground truth data does not contain any tagkey/value mapping conditions:")
print("{:.2f}%".format(len([1 for i in df_data['event_metadata'] if i['tag_key'] == []]) / df_data.shape[0] * 100))
print()

# check if raw event tagkeys are contained by retrieved event tagkeys

contained_raw_events = []
for i in range(df_data.shape[0]):
    is_contained = all(item in retrieved_event_tagkeys[i] for item in raw_event_tagkeys[i])
    contained_raw_events.append(is_contained)

print("the precentage that ground truth data is not contained by retrieved data:")
print("{:.2f}%".format((1-np.average(contained_raw_events)) * 100))
print()
print()

# check details by random seed

print("****** randomly return a sample to check ******")
print()

from random import randint
from random import choice

# idx = randint(0, df_data.shape[0]-1)
idx = choice(list(df_data.index))
print("event name (input for llm):", df_data['event_name'][idx])
print()
print("ground truth:", "\n", df_data['event_metadata'][idx])
print()
print("llm output:", "\n", df_data['pred_event_metadata'][idx])
print()
print("idx =", idx)
