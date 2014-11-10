#! /bin/bash

localedef --list-archive | grep -v -i ^en | xargs localedef --delete-from-archive
mv /usr/lib/locale/locale-archive /usr/lib/locale/locale-archive.tmpl
build-locale-archive
