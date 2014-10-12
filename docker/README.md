firewalld and docker workaround
===============================

Docker Fedora package seems to start docker.service too soon. When it starts,
it locks xtables, and that can prevent firewalld service to start. Adding
Wants/After=network-online.target seems to be fine.

Without this fix, and surely under some random timing conditions, firewalld
complains after boot with INVALID_ZONE messages. /var/log/firewalld reveals
following error with debug level 2 :

    2014-10-12 12:01:52 DEBUG2: firewall.core.ipXtables.ip4tables: /sbin/iptables -t nat -N POSTROUTING_ZONES
    2014-10-12 12:01:52 Traceback (most recent call last):
      File "/usr/lib/python2.7/site-packages/firewall/server/decorators.py", line 40, in handle_exceptions
        return func(*args, **kwargs)
      File "/usr/lib/python2.7/site-packages/firewall/server/firewalld.py", line 78, in start
        return self.fw.start()
      File "/usr/lib/python2.7/site-packages/firewall/core/fw.py", line 253, in start
        self._start()
      File "/usr/lib/python2.7/site-packages/firewall/core/fw.py", line 158, in _start
        self._apply_default_rules()
      File "/usr/lib/python2.7/site-packages/firewall/core/fw.py", line 525, in _apply_default_rules
        self.__apply_default_rules(ipv)
      File "/usr/lib/python2.7/site-packages/firewall/core/fw.py", line 514, in __apply_default_rules
        self.rule(ipv, _rule)
      File "/usr/lib/python2.7/site-packages/firewall/core/fw.py", line 586, in rule
        return self._ip4tables.set_rule(rule)
      File "/usr/lib/python2.7/site-packages/firewall/core/ipXtables.py", line 156, in set_rule
        return self.__run(rule)
      File "/usr/lib/python2.7/site-packages/firewall/core/ipXtables.py", line 152, in __run
        " ".join(_args), ret))
    ValueError: '/sbin/iptables -t nat -N POSTROUTING_ZONES' failed: Another app is currently holding the xtables lock. Perhaps you want to use the -w option?

