from pymongo import MongoClient

# Connect to your MongoDB Atlas
client = MongoClient("your_mongodb_connection_string")  # Replace this with your actual connection string
db = client["your_database_name"]
collection = db["your_collection_name"]

# Sample SVG content (you can use a real SVG file too)
svg_content = """
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="100" cy="100" r="80" fill="lightblue" stroke="black" stroke-width="2"/>
  <text x="50" y="105" font-size="20" fill="black">PUNE</text>
</svg>
"""

# Insert the document
document = {
    "_id": "PUNE_1",
    "svg": svg_content
}

collection.insert_one(document)
print("Inserted PUNE_1 test SVG into MongoDB!")
