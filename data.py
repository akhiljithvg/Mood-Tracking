import firebase_admin
from firebase_admin import credentials, firestore

# Use the application default credentials (replace with your credentials file)
cred = credentials.Certificate('D:/apps/Desktop/Moodtrack/firebase_config/firebase-adminsdk.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Fetch data from a specific collection
collection_ref = db.collection('mood_data')
docs = collection_ref.stream()

for doc in docs:
    print(f'{doc.id} => {doc.to_dict()}')
