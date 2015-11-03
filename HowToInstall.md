

# Using easy\_install #

If you are using pythonenv or don't need special root access to install:

```
   $ easy_install trepan
```

If you need root access you may insert `sudo` in front or become root

```
   $ sudo easy_install trepan
```

or
```
   $ su root
   # easy_install trepan
```


# Using pip #

```
   pip install trepan
```


# From source #

```
    $ git clone https://github.com/rocky/python2-trepan.git # for Python 2.x
    $ git clone https://code.google.com/p/python3-trepan python-trepan # for Python 3.x
    $ cd python-trepan
    $ make check-short # to run tests
    $ make install # if pythonbrew or you don't need root access
    $ sudo make install # if pythonbrew or you do need root access
```

Above I used GNU "make" to run and install. However this just calls `python setup.py` to do the right thing. So if you are more familiar with `setup.py` you can use that directly. For example:

```
    $ ./setup.py test
    $ ./setup.py install 
```
