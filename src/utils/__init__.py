from .parse_boolean import parse_boolean
#from .util import update_record, delete_record,
from .util import *
from .log_impl import *
from .AppConfig import AppConfig
from .FetchError import FetchError
from .version import __version__, __gitversion__
from .types import RRType, FQDN, IPHost, RR_A, RR_TXT, RR_PTR, RRset

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# !! This is applicable only when the end-user imports the module with the `*`
# syntax; `from utils import *`
__all__ = [
  'parse_boolean',
  'reverse_ip',
  'update_record',
  'delete_record',
  'run_cmd',
  'short_hostname',
  'canonical_dns_name',
  'message',
  'crit',
  'error',
  'warn',
  'verbose',
  'log_debug',
  'verbose_debug',
  'debug_trace',
  'AppConfig',
  'FetchError',
  '__version__',
  '__gitversion__',
  #'strclass',
  'RRType',
  'FQDN',
  'IPHost',
  'RR_A',
  'RR_TXT',
  'RR_PTR',
  'RRset',
]
