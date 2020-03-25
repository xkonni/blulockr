blulockr
========


introduction
------------

automatically lock/unlock desktop based on a nearby bluetooth device

- based on https://github.com/LethalEthan/Bluetooth-Unlock


installation
------------

install dependencies with poetry

```bash
$ poetry install
```

- install pybluez with pip (for "reasons" this does not work as a poetry dependency)

```bash
$ poetry shell
$ pip3 install pybluez
```

- allow users to execute l2ping

```bash
$ ./setup.sh
```


usage
-----

- help

```bash
$ blulockr -h
```

- scan for bluetooth devices

```bash
$ sudo blulockr -s
```

- run, using

  - a detected bluetooth device
  - the loginctl backend

```bash
$ sudo blulockr -b 00:11:22:33:44:55 -t loginctl
```
