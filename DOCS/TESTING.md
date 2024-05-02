# PyGDO Testing

Core tests are inside the [/gdotest/](../gdotest) folder.
Extensions are in test folders of the extension module.
You need a configuration in **protected/config_test.toml**

In PyCharm you can right-click a single test method and test only that method.

## Run all unit tests.

Run all core and extension unit tests with a single command.

`python3 gdotestall.py`


## Run core unit tests

The following command runs all core unit tests.

`python3 gdotest.py`

## Run only extension unit tests

Run only extension tests.
This requires you to have a working installation from core testing or similar.

`python3 gdotestothers.py`
