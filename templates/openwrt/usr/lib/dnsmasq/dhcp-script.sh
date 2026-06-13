#!/bin/sh

[ -n "$DNSMASQ_LOG_DHCP" ] && echo "DNSMASQ_LOG_DHCP=$DNSMASQ_LOG_DHCP"; echo
[ -n "$DNSMASQ_LOG_DHCP" ] && echo "USER_DHCPSCRIPT=$USER_DHCPSCRIPT"; echo

load_dhcpscript() {
  CMD="$1"
  if [ -n "$DNSMASQ_LOG_DHCP" ]; then
    echo "$0 - $CMD event"
    echo "$0 - MACADDR=$2"
    echo "$0 - IPADDR=$3"
    echo "$0 - HOSTNAME=$4"
  fi

  if [ "$CMD" = "add" ]; then
    echo "DEBUG: (all arguments): " "$@"
    [ -f "$USER_DHCPSCRIPT" ] && . "$USER_DHCPSCRIPT" "$1" "$2" "$3" "$4"
  elif [ "$CMD" = "del" ]; then
    echo "DEBUG: (all arguments): " "$@"
    [ -f "$USER_DHCPSCRIPT" ] && . "$USER_DHCPSCRIPT" "$1" "$2" "$3" "$4"
  fi
}

load_dhcpscript "$@"

. /usr/share/libubox/jshn.sh

json_init
json_add_array env
hotplugobj=""

case "$1" in
	add | del | old | arp-add | arp-del)
		json_add_string "" "MACADDR=$2"
		json_add_string "" "IPADDR=$3"
    # TODO(JEFF): We ought to sound an alarm when our Python script is
    # installed, activated but not being executed during the ADD and DEL
    # events. At the minimum, a CRITICAL level error message to be found in
    # the logs should be done.
    #echo "DHCPSCRIPT=$USER_DHCPSCRIPT"
	;;
esac

case "$1" in
	add)
		json_add_string "" "ACTION=add"
		json_add_string "" "HOSTNAME=$4"
		hotplugobj="dhcp"
	;;
	del)
		json_add_string "" "ACTION=remove"
		json_add_string "" "HOSTNAME=$4"
		hotplugobj="dhcp"
	;;
	old)
		json_add_string "" "ACTION=update"
		json_add_string "" "HOSTNAME=$4"
		hotplugobj="dhcp"
  ;;
	arp-add)
		json_add_string "" "ACTION=add"
		hotplugobj="neigh"
	;;
	arp-del)
		json_add_string "" "ACTION=remove"
		hotplugobj="neigh"
	;;
	tftp)
		json_add_string "" "ACTION=add"
		json_add_string "" "TFTP_SIZE=$2"
		json_add_string "" "TFTP_ADDR=$3"
		json_add_string "" "TFTP_PATH=$4"
		hotplugobj="tftp"
	;;
esac

json_close_array env

[ -n "$hotplugobj" ] && ubus call hotplug.${hotplugobj} call "$(json_dump)"
