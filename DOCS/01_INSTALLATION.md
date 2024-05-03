# PyGDO Installation

A complete installation procedure is listed here.

You might want to skip to [Install PyGDOv8](#install-pygdov8)


## Dependencies

Required:

- git
- Linux or Windows (untested)
- MariaDB or MySQL
- Python 3.10
- Some python libraries ([requirements.txt](../requirements.txt))

Optionally:

- PyCharm
- Apache 2.4 **WSGI**
- nginx (untested)


## Install Pre-Requisites

This section describes installing the required system software.

### Install linux

A debian based linux distribution is used during development.

### Install git

Windows users have to install [git4windows](https://git-scm.com/download/win).
They will not regret this.
TODO: Tell them nice git4win setup settings.

```
aptitude install git
```

### Install apache2.4

I highly can recommend mpm_itk.
Required is mod_wsgi.

Windows users should try [wampserver]()

### Install MariaDB

### Install Python3.10

### Install required Python3 packages

## Install PyGDOv8

To install this software you should use the `./gdo_adm.sh` utility,
but first you need to download pygdo.

### Download pygdo

```
cd webroot
git clone https://github.com/gizmore/pygdo
cd pygdo
```

### Create protected/config.toml

Create a default config in `protected/config` and edit the file afterwards.

```
cd pygdo
./gdo_adm.sh configure
```

Planned: `./gdo_adm.sh configure --interactive`

### Create a database

```
./gdo_adm.sh database --mysql # This will only print a little help.
```

### Download more modules

To get an overview of available extension modules, and to clone them,
you can use the gdo_adm provide command:

```
./gdo_adm.sh provide # To list all modules
```

```
./gdo_adm.sh provide login,irc # To clone more modules
```

This will clone the modules and their dependencies.

### Install modules

After you cloned everything, you can install modules with the install command:

```
./gdo_adms.sh install --all
```

This will install all modules available on the file system.
If you want to omit some modules, specify them.
Dependencies are resolved.

```
./gdo_adm.sh install irc,log*
```

### PyGDO WSGI

PyGDO supports WSGI for the HTML render mode.
All requests are routed through [index.py](../index.py).

#### Apache2.4

```
./gdo_adm.sh webserver --apache
```

Follow the instructions

My localhost config:

```
<VirtualHost *:80>
	WSGIScriptReloading Off
	WSGIProcessGroup pygdo
	WSGIDaemonProcess pygdo user=gizmore group=gizmore threads=5 python-home=/usr/ home=/home/gizmore/PycharmProjects/pygdo/
        WSGIScriptAlias / /home/gizmore/PycharmProjects/pygdo/index.py  process-group=pygdo application-group=%{GLOBAL}
        ServerName py.giz.org
        AllowEncodedSlashes NoDecode
        DocumentRoot /home/gizmore/PycharmProjects/pygdo/
	<Directory "/home/gizmore/PycharmProjects/pygdo/">
                Options +FollowSymLinks +Indexes +ExecCGI
                AllowOverride All
                Require all granted
        </Directory>
        ErrorLog /home/gizmore/www/pygdo.error.log
        CustomLog /home/gizmore/www/pygdo.access.log combined
</VirtualHost>
```

TODO: NGINX

---

## Optional installation process

### Setup pygdo command

**Optional**:

Add `pygdo/bin/` to your PATH environment variables.

TODO: Windows users explaination.

Follow the instructions of

```
./gdo_adm.sh setenv
```

There is an `-x` switch to just do it.

### Test the installation

**Optional**:

Test with:

```
python3 bin/pygdo.py echo Hello world
```

With environment PATH enabled:

```
pygdo echo Hello World
```

---

## Test more

Read the TESTING chapter of this documentation.

