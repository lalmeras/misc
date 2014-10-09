http_port 8123
acl lan src all
http_access allow lan
http_access deny all
pid_filename __HERE__/run/squid.pid
access_log stdio:__HERE__/log/access.log
cache_log __HERE__/log/cache.log
cache_dir aufs __HERE__/cache 500 256 256
minimum_object_size 2 KB
maximum_object_size 100 MB 
