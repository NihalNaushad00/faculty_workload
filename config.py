import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'ktu_s6_mini_project_secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'faculty.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False