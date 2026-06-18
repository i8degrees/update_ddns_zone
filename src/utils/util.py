#!.venv/bin/python3
# util.py
#
#
# ?? FIXME errors from mypy

from collections import namedtuple
from enum import Enum
import json
import os
import urllib3
import sys
# !! TODO(JEFF): Refactor logging functions to utilize `logging` Python module
# !! import logging
from typing import Final # type: ignore

from .parse_boolean import *
import logging
from .FetchError import FetchError

env = {
    **os.environ
}

env.setdefault("DEBUG", "")
env.setdefault("DEBUG_TRACE", "")
env.setdefault("VERBOSE", "")
env.setdefault("SYSLOG", "")
env.setdefault("PDNS_API_VERSION", "4.8.4")

log = logging.getLogger(__name__)

def reverse_ip(ip_addr) -> str:
    result = str("")
    ip_list = str(ip_addr).split(".")
    ip_list.reverse()
    result = '.'.join(ip_list)
    return result

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

# Update the given DNS zone with the given RR and related data.
#
# params api_url - ... [^10]
# params zone - required string that *must* end with a period character [^20]
# params key - required string containing the passphrase set with `api-key` [^30]
# params req - ... [^40] [^45]
#
# returns integer - zero signifies success (HTTP/1.1 204 No Content)
#
# error 400 - BAD REQUEST due to invalid JSON body from client
# error 400 - BAD REQUEST due to JSON body from client is not a hash
# error 422 - HTTP/1.1 422 UNPROCESSABLE ENTITY
#
# [^10]: https://doc.powerdns.com/authoritative/http-api/index.html#
# [^20]: https://doc.powerdns.com/authoritative/http-api/zone.html#
# [^30]: https://doc.powerdns.com/authoritative/http-api/index.html#enabling-the-api
# [^40]: https://doc.powerdns.com/authoritative/http-api/zone.html#rrset
# [^45]: https://doc.powerdns.com/authoritative/http-api/zone.html#creating-new-rrset
def update_record(url: str, zone: str, api_key: str, json_data: str) -> FetchError:
    err = FetchError(-1, "HTTP/1.1 UNKNOWN")
    request_headers = {}

    request_headers.setdefault("Content-Type", "application/json; charset=utf-8")
    request_headers.setdefault("X-API-Key", "")

    if api_key and len(api_key) > 0:
        request_headers["X-API-Key"] = api_key
    else:
        err.set_message("Missing X-API-Key")
        err.set_code(1)
        return err

    if url and len(url) > 0:
        api_url = url + "/"
    else:
        err.set_message("Missing api_url")
        err.set_code(11)
        err.set_stack({
            "headers": request_headers,
            "api_url": "zero-length"
        })
        return err

    if zone and len(zone) > 0:
        api_url += zone
    else:
        err.set_message("Missing update zone")
        err.set_code(111)
        err.set_stack({
            "headers": request_headers,
            "api_url": api_url,
            "zone": "zero-length",
        })
        return err

    # !! TODO(JEFF): We must construct the JSON input inside this function, instead
    # !! of in the main executable as we have been doing.
    # ?? TODO(JEFF): Validate JSON input
    request_data = json.dumps(json_data).encode('utf-8')

    res = _fetch(url=api_url, headers=request_headers, method="PATCH", body=request_data)

    if res and res.status:
        # >> 1. https://httpwg.org/specs/rfc9110.html#overview.of.status.codes
        err.set_code(res.status)
    if res.status == 200: # Success!
        err.set_message("HTTP/1.1 200 OK")
    if res.status == 204: # Success!
        err.set_message("HTTP/1.1 204 NO CONTENT")
    elif res.status == 400:
        # due to invalid JSON body
        # due to JSON body from script is not a hash (???)
        err.set_message("HTTP/1.1 400 BAD REQUEST")
    elif res.status == 401:
        err.set_message("HTTP/1.1 UNAUTHORIZED")
    elif res.status == 403:
        err.set_message("HTTP/1.1 FORBIDDEN")
    elif res.status == 404:
        err.set_message("HTTP/1.1 404 NOT FOUND")
    elif res.status == 405:
        err.set_message("HTTP/1.1 405 METHOD NOT ALLOWED")
    elif res.status == 422:
        err.set_message("HTTP/1.1 422 UNPROCESSABLE ENTITY")

    return err

# !! WARNING(JEFF): This is subject to change, or even be removed all together!
def delete_record(url, zone_str, api_key, data):
    err = FetchError(-1, "HTTP/1.1 UNKNOWN")
    request_headers = {}

    request_headers.setdefault("Content-Type", "application/json; charset=utf-8")
    request_headers.setdefault("X-API-Key", "")

    if api_key and len(api_key) > 0:
        request_headers["X-API-Key"] = api_key
    else:
        err.set_message("Missing X-API-Key")
        err.set_code(1)
        return err

    if url and len(url) > 0:
        api_url = url + "/"
    else:
        err.set_message("Missing api_url")
        err.set_code(11)
        err.set_stack({
            "headers": request_headers,
            "api_url": "zero-length"
        })

        return err

    if zone and len(zone) > 0:
        api_url += zone
    else:
        err.set_message("Missing update zone")
        err.set_code(111)
        err.set_stack({
            "headers": request_headers,
            "api_url": api_url,
            "zone": "zero-length",
        })
        return err

    # !! TODO(JEFF): We must construct the JSON input inside this function, instead
    # !! of in the main executable as we have been doing.
    # ?? TODO(JEFF): Validate JSON input
    request_data = json.dumps(data).encode('utf-8')
    #request_data["rrsets"][0]["changetype"] = "DELETE"

    res = _fetch(api_url, request_headers, request_data, "DELETE")
    #res = requests.patch(api_url, headers=request_headers, data=request_data)
    if parse_boolean(env["DEBUG"]) == True:
        print("RES:", res.json)
    if res and res.status:
        # >> 1. https://httpwg.org/specs/rfc9110.html#overview.of.status.codes
        err.set_code(res.status)
    if res.status == 200: # Success!
        err.set_message("HTTP/1.1 200 OK")
    if res.status == 204: # Success!
        err.set_message("HTTP/1.1 204 NO CONTENT")
    elif res.status == 400:
        # due to invalid JSON body
        # due to JSON body from script is not a hash (???)
        err.set_message("HTTP/1.1 400 BAD REQUEST")
    elif res.status == 401:
        err.set_message("HTTP/1.1 UNAUTHORIZED")
    elif res.status == 403:
        err.set_message("HTTP/1.1 FORBIDDEN")
    elif res.status == 404:
        err.set_message("HTTP/1.1 404 NOT FOUND")
    elif res.status == 405:
        err.set_message("HTTP/1.1 405 METHOD NOT ALLOWED")
    elif res.status == 422:
        err.set_message("HTTP/1.1 422 UNPROCESSABLE ENTITY")

    return err

# !! FIXME(JEFF): This function is incomplete and should not yet be used!
# ?? TODO(JEFF): Verify what exactly the use of the `inspect` module offers us!
#
# USAGE
# run_cmd("/bin/echo", "hi \a")
#
def run_cmd(program: str, program_args = [], program_mode = 600):
    cmd = str(program)
    if parse_boolean(env["DEBUG"]) == True:
        return os.spawnv(file = cmd, args = program_args, mode = program_mode)
    else:
        pass
        #return inspect.os.spawnv(file = cmd, args = program_args, mode = program_mode)

def short_hostname(hostname: str) -> str:
    host = hostname.split(".")
    return host[0]

def canonical_dns_name(hostname: str, omit_final_dot:bool = False) -> str:
    name = str(hostname)
    name_len = len(name)

    if not name.endswith(".") and omit_final_dot == False:
        name += "."
    elif name.endswith(".") and omit_final_dot == True:
      name = name.rstrip(".")
    return name

#RRset = dict({ fqdn: "", rr_type = "", ttl = 60, record = "" })
def update_record_new(url: str, zone: str, api_key: str, RRset: dict) -> int:
    request_headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-API-Key": api_key,
    }

    if len(url) > 0 and len(zone) > 0:
        api_url = url + "/" + zone
    else:
        # ERR
        return 1
    
    type: str = None
    if rr_type.upper() in ["A", "TXT", "PTR"]:
        type = rr_type
    assert type != None
    
    ttl_param: int = 60
    if ttl and ttl > 0:
        ttl_param = ttl
    
    request_data = {
        "rrsets": [{
        "name": f'{fqdn}',
        "type": f'{type}',
        "ttl": f'{ttl}',
        "changetype": "REPLACE",
        "records": [{
            "content": f'{record}',
            "disabled": False
        }]
        }]
    }
    
    # ?? TODO(JEFF): Use the enhanced EXTEND API when PDNS Auth server is newer 
    # ?? than 4.8.4; I am limited to v4.8.4 API until I upgrade the auth server on my end.
    # >> SEE ALSO
    # >> 1. https://doc.powerdns.com/authoritative/http-api/zone.html#adding-a-single-record-to-a-rrset
    if env["PDNS_API_VERSION"] and env["PDNS_API_VERSION"] >= "4.9.12":
        PDNS_CHANGE_TYPE = "EXTEND"

    res = _fetch(api_url, request_headers, "PATCH", request_data)
    
    # >> 1. https://httpwg.org/specs/rfc9110.html#overview.of.status.codes
    res_status_code = res.status_code
    # !! WARNING(JEFF): This is the catch-all response and should never happen!
    res_message = "HTTP/1.1 UNKNOWN"
    
    if res_status_code == 200: # Success!
        res_message = "HTTP/1.1 200 OK"
    if res_status_code == 204: # Success!
        res_message = "HTTP/1.1 204 NO CONTENT"
    elif res_status_code == 400:
        # due to invalid JSON body
        # due to JSON body from script is not a hash (???)
        res_message = "HTTP/1.1 400 BAD REQUEST"
    elif res_status_code == 401:
        res_message = "HTTP/1.1 UNAUTHORIZED"
    elif res_status_code == 403:
        res_message = "HTTP/1.1 FORBIDDEN"
    elif res_status_code == 404:
        res_message = "HTTP/1.1 404 NOT FOUND"
    elif res_status_code == 405:
        res_message = "HTTP/1.1 405 METHOD NOT ALLOWED"
    elif res_status_code == 422:
        res_message = "HTTP/1.1 422 UNPROCESSABLE ENTITY"
    else:
        res_status_code = -1
        res_message = "HTTP/1.1 UNKNOWN"

    response_detail = namedtuple('ResponseDetail', 'status_code, status_message')
    response_detail.status_code = res_status_code
    response_detail.status_message = res_message
    return response_detail

# /usr/lib/python3.14/unittest/utils.py:54
def strclass(cls):
    return "%s.%s" % (cls.__module__, cls.__qualname__)

