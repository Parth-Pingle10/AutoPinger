from pymongo import MongoClient

uri = "mongodb+srv://parthpingle1234:Parth12345@pinger.ldvowke.mongodb.net/"

client = MongoClient(uri)

print("✅ Connected:", client.list_database_names())