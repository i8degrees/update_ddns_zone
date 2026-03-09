
from utils import *

def main() -> int:
    res = parse_boolean("yes")
    assert res == True
    res = reverse_ip("127.0.0.1")
    assert res == "1.0.0.127"
    return 0

# FIXME(JEFF): ?
#main()
