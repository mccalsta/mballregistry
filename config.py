import os

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-key")
    DATABASE = os.path.join(os.path.dirname(__file__), "database.db")
