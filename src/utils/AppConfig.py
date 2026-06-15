
from pathlib import Path

try:
    import yaml # pyyaml (external module)
    has_yaml_module=1
except:
    has_yaml_module=0

import json # builtin module
import logging
from utils.util import canonical_dns_name

# TODO(JEFF): Add try catch that explicitly tries to handle
# FileNotFoundError and JSONDecodeError (with details of why
# the JSON document was invalid). Additionally, UnicodeDecodeError.
def _load_json(path: str = '') -> dict:
    result: dict = {}
    with open(path, 'r', encoding='utf-8') as file:
        result = json.load(file)
        return result

def _load_yaml(path: str = '') -> dict:
    result: dict = {}
    try:
        with open(path, 'r', encoding='utf-8') as file:
            result = yaml.safe_load(file)
            return result
    except UnicodeDecodeError:
        print(f"Failed to decode UTF-8 file at {f}.")
    except FileNotFoundError:
        print(f"YAML file at {f} not found.")

""" AppConfig """
class AppConfig:

    def __init__(self, path: str = '') -> None:
        self._version: int = 0
        self._path = Path(path)
        if has_yaml_module == 1:
            if self._path.suffix == '.yml' or self._path.suffix == '.yaml':
                self.app = _load_yaml(self._path)
                self._fmt = 'yaml'
        elif has_yaml_module == 0:
            self.app = None
            self._fmt = ""
        if self._path.suffix == '.json':
            self.app = _load_json(self._path)
            self._fmt = 'json'
        if self.app and self.app["version"]:
            #self._version: int = self.app["version"]
            self.set_version(self.app["version"])
        assert self._version != 0, \
            "self._version should never == 0 without _load_yaml throwing exception!"

    def fmt(self) -> str:
        """Return the language used to parse the configuration file"""
        return self._fmt; # (yaml|json|"")
    def path(self) -> str:
        return self._path

    def set_path(self, path_str: str = '') -> None:
        self._path = path_str

    def dump(self) -> dict:
        return self.app

    def version(self) -> int:
        return self._version
    
    def set_version(self, ver: int) -> None:
        self._version = ver
    
    # >> private
    def _dump_forward_ddns(self) -> dict:
        result: dict = {}
        if self.app: #and type(self.app) == 'dict':
            result = self.app.get("forward-ddns")
        return result
    
    # >> private
    def _dump_reverse_ddns(self) -> dict:
        result: dict = {}
        if self.app: #and type(self.app) == 'dict':
            result = self.app.get("reverse-ddns")
        return result
    
    # >> private
    def _dump_forward_ddns_zones(self) -> dict:
        result: dict = {}
        if self.app: #and type(self.app) == 'dict':
            rcfg = self._dump_forward_ddns()
            if self.version() == 1:
                result = rcfg.get("ddns-domains")
            elif self.version() >= 2:
                result = rcfg.get("domains")
            
        return result
    
    # >> private
    def _dump_reverse_ddns_zones(self) -> dict:
        result: dict = {}
        if self.app: #and type(self.app) == 'dict':
            rcfg = self._dump_reverse_ddns()
            if self.version() == 1:
                result = rcfg.get("ddns-domains")
            elif self.version() >= 2:
                result = rcfg.get("domains")
        return result
    
    # ?? Rename to find_zone
    def lookup_forward(self, label: str) -> str:
        zones = self._dump_forward_ddns_zones()
        for cfg in zones:
          zone_key = cfg.get("name")
          if zone_key == label:
              return cfg
    # ?? Rename to find_ptr_zone
    def lookup_reverse(self, label: str) -> str:
        zones = self._dump_reverse_ddns_zones()
        for cfg in zones:
          zone_key = cfg.get("name")
          if zone_key == label:
              return cfg
    # ?? Impl? If so, we ought to check for `type(self.app) == dict`, right?
    #def get(self, value):
        #return self.app.get(value)

    def options(self) -> str:
        result: dict = {}
        if self.app: #and type(self.app) == 'dict':
            result = self.app.get("global-config")
        return result

    def api_host(self) -> str:
        result: dict = {}
        if self.app:
            rcfg = self.options()
            if rcfg:
                result = rcfg.get("api_host")
                
        return result
