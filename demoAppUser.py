from appInterface import ApplicationInterface
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


API_URL = "http://192.168.0.219:8000/ec/payloads"
API_URL = "http://192.168.56.1:8000/ec/payloads"
interface = ApplicationInterface(API_URL)


# GET IP OF THE APP GIVEN THE NAME
APPNAME="demoAppPrediction"
appIP = interface.getAppIPbyName(APPNAME)['data']
print("[+] AppIP:", appIP)

appUSE = interface.getAppUsebyName(APPNAME)['data']
print("[+] AppUSE: CPU:", appUSE[0], "| RAM:", appUSE[1])

# CALL THE APP
s = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
s.mount('http://', adapter)

_appURL = "http://" + appIP + ":5000/run-app"
resp = s.get(url=_appURL)
print('[+] Message from App:',resp.text)

_appURL = "http://" + appIP + ":5000/hi"
resp = s.get(url=_appURL)
print('[+] Message from App:',resp.text)
