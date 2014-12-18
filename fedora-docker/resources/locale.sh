#! /bin/bash

# -a is needed as list-archive output may be binary
localedef --list-archive | grep -a -v -i ^en | xargs localedef --delete-from-archive
mv /usr/lib/locale/locale-archive /usr/lib/locale/locale-archive.tmpl
build-locale-archive
