
import json
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Update the URI as needed
db = client["sports_analysis"]  # Database name
collection = db["video_data"]  # Collection name

# Load the JSON file
with open(r"data\processed_videos (4).json", "r") as file:
    videos = json.load(file)

# Process and insert each video dataset
for video_data in videos:
    # Transform data into the desired schema
    transformed_data = {
        "video_name": video_data.pop("video_name"),
        "entities": [
            {
                "id": int(entity_id),
                "type": entity["type"],
                "distance": entity["distance"],
                "speed": entity["speed"]
            }
            for entity_id, entity in video_data.items()
        ]
    }
    
    # Insert into MongoDB
    result = collection.insert_one(transformed_data)
    print(f"Inserted video '{transformed_data['video_name']}' with ID: {result.inserted_id}")

# %%
