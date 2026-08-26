import os

class Config:
    SECRET_KEY = 'gamehub-secret-123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///gamehub.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False