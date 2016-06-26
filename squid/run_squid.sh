#! /bin/bash

SCRIPT="$(readlink -f $0)"
HERE="$(dirname "$SCRIPT")"

sed "s@__HERE__@$HERE@" "${HERE}/squid.conf.tpl" > "${HERE}/squid.conf"

if [ ! -f "$HERE/ssl_cert/myCA.pem" ]; then
	openssl req -new -newkey rsa:2048 -sha256 -days 365 -nodes -x509 -keyout "$HERE/ssl_cert/myCA.pem" -out "$HERE/ssl_cert/myCA.pem"
fi

if [ ! -d "$HERE/ssl_db" ]; then
	/usr/lib64/squid/ssl_crtd -c -s "$HERE/ssl_db/"
fi

if which squid > /dev/null; then
	SQUID=squid
elif which squid3 > /dev/null; then
	SQUID=squid3
fi

if [ ! -f "${HERE}/cache/swap.state" ]; then
	echo "Initializing cache..."
	$SQUID -f "${HERE}/squid.conf" -z -N
	echo "Cache initialized."
else
	$SQUID -f "${HERE}/squid.conf" -z -N
fi


if which multitail > /dev/null 2>&1; then
	$SQUID -f "${HERE}/squid.conf" -N 2>&1 | multitail -j --retry-all -i "${HERE}/log/cache.log" "${HERE}/log/access.log"
else
	$SQUID -f "${HERE}/squid.conf" -N
fi
