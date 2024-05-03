# PyGDO Installation

A complete installation procedure is listed here.

You might want to skip to [Install PyGDOv8](#install-pygdov8)


## Dependencies

- Linux
- git
- Apache 2.4 **WSGI** (nginx unknown)
- MariaDB or MySQL
- Python 3.10 (not exactly known)
- Some python libraries ([requirements.txt](../requirements.txt))

Optionally i recommend PyCharm from JetBrains.


## Install Pre-Requisites

This section describes installing the required system software.


### Install linux

A debian based linux distribution is used during development.

### Install git

`aptitude install git`

### Install apache2.4

I highly can recommend mpm_itk.
Required is mod_wsgi.


### Install MariaDB

### Install Python3.10

### Install required Python3 packages

## Install PyGDOv8

To install this software you should use the `./gdo_adm.sh` utility,
but first you need to download pygdo.

### Download pygdo

`cd webroot`

`git clone https://github.com/gizmore/pygdo`

`cd pygdo`

### Create protected/config.toml

Create a default config in `protected/config` and edit the file afterwards.

`cd pygdo`

`./gdo_adm.sh configure` or `./gdo_adm.sh configure --interactive`

### Create a database

`cd pygdo`

`./gdo_adm.sh database`

Follow the instructions.

### Download more modules

(TODO)

Example: `./gdo_adm.sh provide login,irc

### Install modules

`./gdo_adms.h install --all`

## Optional installation process

### Setup pygdo PATH variable

Optional:

Follow the instructions of `./gdo_adm.sh setenv` or use `./gdo_adm.sh setenv -x`.


### Test the installation

Optional:

Test with:

`python3 bin/pygdo.py echo Hello world`

With environment PATH enabled:

`pygdo echo 1`

## Test more
