#! /bin/bash

SCRIPT="$(realpath -e $0)"
HERE="$(dirname "$SCRIPT")"

sed "s@__HERE__@$HERE@" "${HERE}/squid.conf.tpl" > "${HERE}/squid.conf"

if which multitail > /dev/null 2>&1; then
	squid -f "${HERE}/squid.conf" -N 2>&1 | multitail -j --retry-all -i "${HERE}/log/cache.log" "${HERE}/log/access.log"
else
	squid -f "${HERE}/squid.conf" -N
fi
