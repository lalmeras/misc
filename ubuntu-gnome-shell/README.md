Gnome shell & Ubuntu
====================

Workaround to use gnome-shell and ubuntu

Black widgets
-------------

Default Ambiance gtk theme and Adwaita gtk theme are messed up by black
backgrounds. It can be fixed by disabling scrollbar overlays (useless if
gnome-shell is used).

        gsettings set com.canonical.desktop.interface scrollbar-mode normal

Original setting (auto) can be retrieved with

        gsettings reset com.canonical.desktop.interface scrollbar-mode

