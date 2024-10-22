import os


class Config:
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "test")
    MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://test:Password1!@mongodb-0.mongodb-headless.default.svc.cluster.local:27017/?replicaSet=rs0&authSource=test")
    ELLIS_APP_EVENT_COLLECTION = os.getenv("ELLIS_APP_EVENT_COLLECTION", "ellis_app_event")
    ELLIS_JOB_EVENT_COLLECTION = os.getenv("ELLIS_JOB_EVENT_COLLECTION", "ellis_job_event")
