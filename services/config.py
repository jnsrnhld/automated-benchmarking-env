import os


class Config:
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "test")
    MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://test:Password1!@mongodb-0.mongodb-headless.default.svc.cluster.local:27017/?replicaSet=rs0&authSource=test")
