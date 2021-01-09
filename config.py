import os
from dotenv import load_dotenv
import datetime


def load_vars():
    try:
        postgres = os.environ['DATABASE_URL']
        token = os.environ['TOKEN']
        print(os.environ['TZ'])
        print("time is ", datetime.datetime.now())
        print('loaded heroku env variables')
    except KeyError:
        load_dotenv()
        print('loaded local dotenv file')
        postgres = os.environ['uri']
        token = os.environ['token']
    return postgres, token
