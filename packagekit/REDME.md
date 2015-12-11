Disable PackageKit
==================

PackageKit interferes with distribution packaging manager (redondant
package cache and download).

To get rid of PackageKit :

```
sudo systemctl disable packagekit.service
```
