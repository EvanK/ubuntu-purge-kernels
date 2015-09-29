# Why is this necessary?

In most cases, it isn't -- running `apt-get autoremove` should identify and remove old packages (including old kernels).

# Then _when_ is this necessary?

Ubuntu's package manager has to read from and write to the `/boot` directory in order to autoremove old kernels, and if there is insufficient space to do this, the package manager will fail with rather cryptic error messages.

The sure fire remedy is to carefully find and remove the old kernels by hand and then update the boot loader, [as explained in this Stack Exchange post](http://askubuntu.com/questions/345588/what-is-the-safest-way-to-clean-up-boot-partition#answer-430944).

Instead, you can run the included python script (requires root or sudo permission). By default, it will short circuit unless the `/boot` directory is 75% or more full:

```
root@localhost# ./purge-kernels.py
$ df -k /boot

$ du -ks /boot

Boot partition is only 74% full
```

You can override this by passing a minimum percentage as an argument:

```
root@localhost# ./purge-kernels.py 50
$ df -k /boot

$ du -ks /boot

$ dpkg --list "linux-image*"

$ uname -r

Found: 3.13.0-57

Found: 3.13.0-58

Found: 3.13.0-59

$ ls -1 /boot/*-3.13.0-57-*

Removing:
/boot/abi-3.13.0-57-generic
/boot/config-3.13.0-57-generic
/boot/initrd.img-3.13.0-57-generic
/boot/System.map-3.13.0-57-generic
/boot/vmlinuz-3.13.0-57-generic

$ rm -rf /boot/*-3.13.0-57-*

$ update-grub

```

