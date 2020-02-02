import requests

class Airhorn(object):
    """Docstring for Airhorn. """

    def __init__(self, pid, tid, url = "https://data.sensor.community/airrohr/v1/sensor/{id}/"):
        self.pid = pid
        self.tid = tid
        self.url = url

    def get_data(self): 
        try:
            retval = dict()
            retval.update( self._get_temperature() )
            retval.update( self._get_pvalues() )
            return retval
        except (requests.ConnectionError, requests.HTTPError):
            return dict()

    def _get_temperature(self):
        r = requests.get(self.url.format(id = self.tid))
        jr = r.json()
        return {
                "temperature": jr[0]["sensordatavalues"][0]["value"],
                "humidity": jr[0]["sensordatavalues"][1]["value"]
            }

    def _get_pvalues(self):
        r = requests.get(self.url.format(id = self.pid))
        jr = r.json()
        return {
                "p10": jr[0]["sensordatavalues"][0]["value"],
                "p2.5": jr[0]["sensordatavalues"][1]["value"]
            }
