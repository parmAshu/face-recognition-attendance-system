# Install the packages

`sudo apt update`
`sudo apt install network-manager network-manager-gnome`

# Configure dhcpd to ingore wlan0 ( or whatever interface is to be used with nmcli )

The `/etc/network/interfaces` file should be empty except for an include from `/etc/network/interfaces.d` (which in turn is empty).

Add the following line to `/etc/dhcpcd.conf` :

`denyinterfaces wlan0`

# Configure the Network Manager to control wlan0 and assume dhcp duties

Put the following in the file `/etc/NetworkManager/NetworkManager.conf` :

`[main]`<br>
`plugins=ifupdown,keyfile`<br>
`dhcp=internal`<br><br>
`[ifupdown]`<br>
`managed=true`

Reboot the system