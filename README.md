# apkchecker

A python lib for running and checking apk file on android device automatically.

## Installation

apkchecker is based on following projects:

* adb: <http://developer.android.com/tools/help/adb.html>
* AndroidViewClient: <https://github.com/dtmilano/AndroidViewClient>

```
# install
pip install -U setuptools  # if needed
easy_install --upgrade androidviewclient
```
* aapt: <https://code.google.com/p/android-apktool/>

## Usage
Write your own config file and run
``` python
python apkcheck.py test_conf.json
```

## License
This project is under the MIT License. See the [LICENSE](LICENSE) file for the full license text.