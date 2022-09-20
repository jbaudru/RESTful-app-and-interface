from appInterface import ApplicationInterface
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_URL = "http://192.168.0.219:8000/"
API_URL = "http://192.168.56.1:8000/"
interface = ApplicationInterface(API_URL)


# GET IP OF THE APP GIVEN THE NAME
APPNAME="demoEdge"
appIP = interface.getAppIPbyName(APPNAME)['data']
print("[+] Edge node IP:", appIP)

#appUSE = interface.getAppUsebyName(APPNAME)['data']
#print("[+] AppUSE: CPU:", appUSE[0], "| RAM:", appUSE[1])


s = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
s.mount('http://', adapter)
_appURL = "http://" + appIP + ":5000/predict"
resp = s.get(url=_appURL)

print('[+] Prediction from the Edge:',resp.text)
