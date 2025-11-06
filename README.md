# pygdo

GDO reference implementation in Python3.

Version 8.0.0

This is proprietary software.

### Documentation

The [documentation](./DOCS/README.md) is work in progress.


### Installation

Please refer to the [INSTALLATION](./DOCS/01_INSTALLATION.md),
but it boils down to:

```
git clone https://github.com/gizmore/pygdo
cd pygdo
pip3 install -r requirements.txt
./gdo_adm.sh configure
nano protected/config.php
./gdo_adm.sh database --mysql -x > sudo mysql  # To create a database
./gdo_adm.sh provide dog_website  # or any other modules wanted
./gdo_adm.sh install --all
./gdo_adm.sh setenv -x
sudo ./gdo_adm.sh webconfig --apache > /etc/apache2/sites-enabled/099_pygdo.conf
/etc/init.d/apache2/restart
./gdo_adm.sh cronjob -x  # if cronjobs are wanted
pygdo echo Hello World!
```


#### [pygdo license](./LICENSE)

The core is only using MIT licensed modules and is licensed under the proprietary GDOv8 license.

Modules are licensed separately.
