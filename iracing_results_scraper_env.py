import json
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

IRACING_USER = os.getenv('IRACING_USER')
IRACING_PASSWORD = os.getenv('IRACING_PASSWORD')

IRACERS_FILE = os.getenv('IRACERS_FILE')
SESSIONS_FILE = os.getenv('SESSIONS_FILE')

REFRESH_RATE = int(os.getenv('REFRESH_RATE'))

if not DISCORD_TOKEN:
    print('Fill the DISCORD_TOKEN environment variable')
    exit(1)
    
if not DISCORD_CHANNEL_ID:
    print('Fill the DISCORD_CHANNEL_ID environment variable')
    exit(1)

if not IRACING_USER:
    print('Fill the IRACING_USER environment variable')
    exit(1)
    
if not IRACING_PASSWORD:
    print('Fill the IRACING_PASSWORD environment variable')
    exit(1)
    
if not IRACERS_FILE:
    print('Fill the IRACERS_FILE environment variable')
    exit(1)
    
if not SESSIONS_FILE:
    print('Fill the SESSIONS_FILE environment variable')
    exit(1)
    
if not REFRESH_RATE:
    print('Fill the REFRESH_RATE environment variable')
    exit(1)
    
iracers_to_query = {}
iracer_to_session_map = {}

def load_iracers_to_query ():
    if not os.path.exists (IRACERS_FILE):
        return
        
    with open (IRACERS_FILE, 'r') as file_handle:
        global iracers_to_query
        iracers_to_query = json.load (file_handle)
        
    print ('Loaded ' + str (len (iracers_to_query.items ())) + ' subscribed users')

def save_iracers_to_query ():
    with open (IRACERS_FILE, 'w') as file_handle:
        json.dump (iracers_to_query, file_handle)

    print ('Saved ' + str (len (iracers_to_query.items ())) + ' subscribed users')

        
def load_iracer_to_session_map ():
    if not os.path.exists (SESSIONS_FILE):
        return

    with open (SESSIONS_FILE, 'r') as file_handle:
        global iracer_to_session_map
        iracer_to_session_map = json.load (file_handle)

    print ('Loaded ' + str (len (iracer_to_session_map.items ())) + ' scanned races')

def save_iracer_to_session_map ():
    with open (SESSIONS_FILE, 'w') as file_handle:
        json.dump (iracer_to_session_map, file_handle)

    print ('Saved ' + str (len (iracer_to_session_map.items ())) + ' scanned races')
