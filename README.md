misc
====

Various configuration files


Inhibit close lid action
------------------------

```
systemd-inhibit --what=handle-lid-switch --who=me --why=because --mode=block /bin/sh
```
