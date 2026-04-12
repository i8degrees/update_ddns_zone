
from utils.types import RRType, FQDN, IPHost, RR_A, RR_TXT, RR_PTR, RRset
#from utils.util import 
from utils.FetchError import FetchError

class PowerDNSAPI:
  def __init__(self, host:str, port: int = 53, passphrase: str) -> None:
    self.api_host = host
    self.api_port = port
    self.passphrase = passphrase
    self.version = "4.8.4"
    self.headers = {}

  def _fetch(url: str, headers: list, method: str, body: dict = {}):
    res = None
    request_headers = {}
    json_data = {}
    http_method = str(method).lower()

    if len(headers) > 0:
        request_headers = headers
    #if len(body) > 0:
        #json_data = json.dumps(body)
    # TODO(JEFF): Check SSL requirements
    # res = urllib3.request(method='PATCH', url='', headers={}, body={})
    # res.code
    # res.json()
    res = urllib3.request(method=http_method, url=url, headers=request_headers, body=body)
    return res

    #if method == "GET":
        #res = requests.get(url, headers=request_headers, data=data)
    #if method == "DELETE":
        #res = requests.delete(url, headers=request_headers, data=data)
    #else: # PATCH
        #res = requests.patch(url, headers=request_headers, data=data)

  
  def update(zone: str, json_data: dict) -> FetchError:
    err = FetchError(-1, "HTTP/1.1 UNKNOWN")
    return err

  def delete(zone: str, json_data: dict) -> FetchError:
    err = FetchError(-1, "HTTP/1.1 UNKNOWN")
    return err

