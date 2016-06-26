# proxy https with MITM
http_port 3128 ssl-bump \
  cert=__HERE__/ssl_cert/myCA.pem \
  generate-host-certificates=on dynamic_cert_mem_cache_size=4MB
sslcrtd_program /usr/lib64/squid/ssl_crtd -s __HERE__/ssl_db -M 4MB

pid_filename __HERE__/run/squid.pid
access_log stdio:__HERE__/log/access.log
cache_log __HERE__/log/cache.log

minimum_object_size 0 KB
maximum_object_size 300 MB
# force cache on basic auth / without cache directive
refresh_pattern . 0 90% 432000 ignore-auth reload-into-ims
# 5Go cache
cache_dir aufs __HERE__/cache 5000 256 256

# ACLs
acl lan src all
acl step1 at_step SslBump1

http_access allow lan
http_access deny all

ssl_bump peek step1
ssl_bump bump all
