# proxy https with MITM
#http_port 3128 ssl-bump \
#  cert=__HERE__/ssl_cert/myCA.pem \
#  generate-host-certificates=on dynamic_cert_mem_cache_size=4MB
#sslcrtd_program /usr/lib64/squid/security_file_certgen -s __HERE__/ssl_db -M 4MB
http_port 3128

pid_filename __HERE__/run/squid.pid
access_log __HERE__/log/access.log
cache_log __HERE__/log/cache.log
cache_store_log __HERE__/log/store.log
#debug_options ALL,2

# 5Go cache
cache_dir aufs __HERE__/cache 7000 256 256
minimum_object_size 0 KB
maximum_object_size 350 MB

# ACLs
acl lan src all
#acl step1 at_step SslBump1

http_access allow lan
http_access deny all

# force cache on basic auth / without cache directive
#refresh_pattern . 0 90% 432000 ignore-auth ignore-reload reload-into-ims

#ssl_bump peek step1
#ssl_bump bump all
