#!.venv/bin/python
import os
import argparse
from utils import __version__, __gitversion__

PROG_NAME = 'ddns_psupdate'
PROG_VERSION = '%(prog)s 1.0.0'
# ?? import utils for __version__ def
PROG_VERSION = '%(prog)s ' + 'v' + __version__ + ' at git SHA ' + __gitversion__
DESCRIPTION = 'Update DNS upon DHCP lease'
DEFAULT_LOG_LEVELS = ["DEBUG", "NOTICE", "INFO", "WARNING", "CRITICAL", "ERROR"]
DEFAULT_CONFIG_FILE_PATH = "config/app.yml"
DEFAULT_LOG_LEVEL = 'INFO'
DEBUG = False
DEFAULT_CMD_OPTS = ["ADD", "OLD", "DEL"]

parser = \
    argparse.ArgumentParser(prog=PROG_NAME, description=DESCRIPTION)
parser.add_argument("CMD", help=f'Command is one of {DEFAULT_CMD_OPTS}')
parser.add_argument("MAC_ADDR", 
                    help="The 48-bit link-layer address")
parser.add_argument("IP_ADDR", nargs=1, 
                    help="Client IPv4 address")
parser.add_argument("HOSTNAME", nargs=1, 
                    help="Client's (short) hostname")
parser.add_argument("-c", "--config", default=DEFAULT_CONFIG_FILE_PATH, 
                    help=f"The file path to the configuration file")
parser.add_argument("-d", "--debug", action="store_true", 
                    help="Enable debugging code")
parser.add_argument("-l", "--log", default=DEFAULT_LOG_LEVEL,
    help=f'Set the log level to one of {DEFAULT_LOG_LEVELS}')
parser.add_argument("-v", "--version", action="version", version=PROG_VERSION)

#parser.print_help()

args = parser.parse_args()

DEBUG = bool(args.debug)
LOG_LEVEL = DEFAULT_LOG_LEVEL
if args.log.upper() in DEFAULT_LOG_LEVELS:
    LOG_LEVEL = args.log.upper()
CMD = args.CMD.upper()
MAC_ADDR = args.MAC_ADDR
IP_ADDR = args.IP_ADDR
HOSTNAME = args.HOSTNAME

#print(args.log)
#print(args.command)
print(f'DEBUG={DEBUG}')
print(f'LOG_LEVEL={LOG_LEVEL}')
#print(args)
print(f'update {CMD} {MAC_ADDR} {IP_ADDR} {HOSTNAME}')

if args.config:
    if not (os.path.isfile(args.config) and os.access(args.config, os.R_OK)):
      print(f"ERROR: The given file path at {args.config} does not exist.")
      exit(1)
    else:
       print(f"Found configuration file at {args.config}")

print("success!")
exit(0)
