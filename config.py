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
        try:
            postgres = os.environ['QOVERY_DATABASE_TRADER_BOT_CONNECTION_URI']
            token = os.environ['token']
            print('loaded qovery vars')
        except KeyError:
            load_dotenv()
            print('loaded local dotenv file')
            postgres = os.environ['uri']
            token = os.environ['token']
    return postgres, token
