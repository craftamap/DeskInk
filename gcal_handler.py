import datetime
import pickle
import configparser
import json
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GcalHandler(object):
    """Docstring for Gcal_Handler. """

    def __init__(self, config):
        self.config = config["gcal"]
        self.calendar_ids = set()
        self._register_multiple_calendar_ids(self.config["ids"])
        creds = pickle.loads(self.config["pickle"].encode("latin1"))
        print(creds)
        self.service = build('calendar', 'v3', credentials=creds,
                             cache_discovery=False)

    def _register_multiple_calendar_ids(self, calendar_ids: str):
        cids = calendar_ids.split(",")
        for cid in cids:
            cid = cid.strip()
            self._register_calendar_id(cid)

    def _register_calendar_id(self, calendar_id):
        self.calendar_ids.add(calendar_id)

    def get_next_appointments(self, limit=3):
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time 
            appointments = []
            for cid in self.calendar_ids:
                print(cid)
                liste = self.service.events().list(calendarId=cid, timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
                appointments.extend(  liste.get('items', []) )
            appointments.sort(key= lambda x: x["start"].get("dateTime", x["start"].get("date")))
            return appointments[:limit]
        except:
            return []


def add_pickle_to_config(decrypted_data: bytes):
    """
    """
    cp = configparser.ConfigParser()
    cp.read_string(decrypted_data.decode())
    credentials = json.loads(cp["gcal"]["credentials"])
    auth = _get_auth_from_browser(credentials)
    cp["gcal"]["pickle"] = pickle.dumps(auth).decode("unicode_escape")
    buf = io.StringIO()
    cp.write(buf)
    return buf.getvalue().encode()


def _get_auth_from_browser(credentials):
    """
    """
    flow = InstalledAppFlow.from_client_config(
        credentials, SCOPES)
    creds = flow.run_local_server(port=0)
    return creds



