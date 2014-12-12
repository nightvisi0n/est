est
===

A console interface for Exercise Submission Tool (https://est.informatik.uni-erlangen.de/)

Installation
------------

* download latest version: `wget https://github.com/jneureuther/est/archive/master.zip`
* unzip downloaded file: `unzip master.zip`
* run: `sudo ./setup.py install`
* run: `sudo activate-global-python-argcomplete` to enable argument completion

Usage
-----

```
usage: est [-h] [-v] {login,search,submit,status} ...

Console Interface to Exercise Submission Tool

positional arguments:
  {login,search,submit,status}
    login               login on est
    search              search a file(s) on est
    submit              submit a file(s) on est
    status              check the status of a given file(s)

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

Example
-------

Submit a File named FooBar.java to EST:
```
est submit FooBar.java
Console Interface to Exercise Submission Tool | Rev1.0
Current EST version is supported.
User: john_doe
Password: 
[i] Successfully signed in with user john_doe!
[i] ✓ Uploading..
[i] Successfully uploaded FooBar.java to Foobar course (Einzelabgabe) (WS 14/15)
[i] ✓ Waiting for test result..
[!] Error in given test case.
```

Dependencies
------------
* python2.7
* libest
* python-requests (2.3.0)
* python-magic
* python-bs4
* python-colorama
* python-configparser
* python-argcomplete

License
-------

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
