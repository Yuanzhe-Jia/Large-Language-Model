!pip install scikit-learn
!pip install sentence_transformers
!pip install pandas

from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import json

# 
# get data
with open('events.json', 'r') as file:
    data = json.load(file)  # parses the JSON to a list

#len(data)

# convert to dataframe
df = pd.DataFrame(data)

# combine event_name and attribute_value for embedding
df['event'] = df['event_name'] + ", " + df['attribute_name'] + ", " + df['attribute_value']

#
# load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# generate embeddings
embeddings = model.encode(df['event'].tolist(), show_progress_bar=True)
#print(embeddings)

#
# hyper-parameter setting!!!
num_clusters = 3
num_events = 100

# apply clustering model
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
df['cluster'] = kmeans.fit_predict(embeddings)
#print(df.shape)

# # # # # # # # # # 

#
# define a function to find the top-n representative events for each cluster
def get_representative_events(df, embeddings, kmeans, top_n):
    representative_events = {}
    for cluster_id in range(kmeans.n_clusters):
        
        # get indices of points in the current cluster
        cluster_indices = np.where(kmeans.labels_ == cluster_id)[0]
        
        # extract embeddings of points in this cluster
        cluster_embeddings = embeddings[cluster_indices]
        
        # compute distances to the cluster centroid
        centroid = kmeans.cluster_centers_[cluster_id]
        distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
        
        # find indices of the top-n closest events to the centroid
        top_indices = cluster_indices[np.argsort(distances)[:top_n]]
        
        # save the most representative events for this cluster
        representative_events[f"cluster {cluster_id}"] = df.iloc[top_indices]['event'].tolist()
    
    return representative_events

# get representative events for each cluster
representative_events = get_representative_events(df, embeddings, kmeans, top_n=num_events)

#
# define context that LLM should know
context = json.dumps(representative_events, indent=4)
#print(context)

# define format that LLM should follow
format_instruction = {
    "cluster 0 name": ["keyword 01", "keyword 02", "keyword 03"],
    "cluster 1 name": ["keyword 11", "keyword 12", "keyword 13"],
    "cluster 2 name": ["keyword 21", "keyword 22", "keyword 23"]
}

# define prompt
prompt = f"""
Role:
You are a professional app analyst, understanding app behaviors very well.

Context:
{context}
The above content contains multiple clusters, each cluster contains multiple rows.
Each row contains 3 fields: the name of the event, an attribute of the event, and a possible value for the attribute.
Each row represents a specific app behavior.
Each cluster represents a set of different app behaviors with great similarity.

Tasks:
Understand the given context and complete the following tasks:
**Step 1**
For each cluster, come out 5 to 10 keywords which represent different app behaviors.
Each keyword should be concise and easy to understand.
Each keyword should be no more than 2 words.
Each keyword should not contain any punctuation.
**Step 2**
Based on the keywords you produced, come out a name for each cluster.
Each cluster name should be abstract and easy to understand.
Each cluster name should be no more than 2 words.
Each cluster name should not contain any punctuation.
**Step 3**
Output a JSON in your response that contains cluster names and their keywords.
The output Json should follow the below format:
{format_instruction}
"""
#print(prompt) # let LLM generate both titles and sub-titles for events

#
# request LLM based on the prompt
import requests

url = "https://.../inference"

# request body
payload = {
    "prompt": prompt
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

# # # # # # # # # # 

#
# hyper-parameter setting!!!
num_clusters = 20
num_events = 100

# apply clustering model
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
df['cluster'] = kmeans.fit_predict(embeddings)
#print(df.shape)

#
# define a function to find the top-n representative events for each cluster
def get_representative_events(df, embeddings, kmeans, top_n):
    representative_events = {}
    for cluster_id in range(kmeans.n_clusters):
        
        # get indices of points in the current cluster
        cluster_indices = np.where(kmeans.labels_ == cluster_id)[0]
        
        # extract embeddings of points in this cluster
        cluster_embeddings = embeddings[cluster_indices]
        
        # compute distances to the cluster centroid
        centroid = kmeans.cluster_centers_[cluster_id]
        distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
        
        # find indices of the top-n closest events to the centroid
        top_indices = cluster_indices[np.argsort(distances)[:top_n]]
        
        # save the most representative events for this cluster
        representative_events[f"cluster {cluster_id}"] = df.iloc[top_indices]['event'].tolist()
    
    return representative_events

# get representative events for each cluster
representative_events = get_representative_events(df, embeddings, kmeans, top_n=num_events)

#
# define context that LLM should know
context = json.dumps(representative_events, indent=4)
#print(context)

# define format that LLM should follow
format_instruction = {
    "Cluster Names": [
        "cluster name 1", 
        "cluster name 2", 
        "cluster name 3"
    ]
}

# define prompt
prompt = f"""
Role:
You are a professional app analyst, understanding app behaviors very well.

Context:
{context}
The above content contains multiple clusters, each cluster contains multiple rows.
Each row contains 3 fields: the name of the event, an attribute of the event, and a possible value for the attribute.
Each row represents a specific app behavior.
Each cluster represents a set of different app behaviors with great similarity.

Tasks:
Understand the given context and complete the following tasks:
**Step 1**
Based on the rows in each cluster, come out a name for each cluster.
Each cluster name should be abstract and easy to understand.
Each cluster name should be no more than 2 words.
Each cluster name should not contain any punctuation.
**Step 2**
Output a Json in your response that contains all of cluster names.
The output Json should follow the below format:
{format_instruction}
"""

#print(prompt) # let LLM generate sub-titles for events

#
# request LLM based on the prompt
import requests

url = "https://.../inference"

# request body
payload = {
    "prompt": prompt
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
