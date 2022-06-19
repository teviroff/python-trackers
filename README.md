# Python Trackers
This is a simple python package, that helps tracking the code execution.

## Getting Started
This project is made to be simple-to-use, open-source package that helps during debugging or executing a high-weight command line applications.

This is PyPI package, so it is downloadable via pip:  
```
> pip install trackers
```

### Using
Imagine you have some for loop, that executes very lazy and you want to track its execution progress.

    for i in range(10): ...  # Some lazy loop

There is a simple solution to your problem:

    for i in ForTracker('lazy loop', range(10)): ... # Tracked loop

The output for this will look like this:

```
> (1/10) lazy loop - 1.08s
```

Other use-cases are presented in module docstrings and on [GitHub](https://github.com/teviroff/python-trackers/wiki)

### Requirements
This package is written using **Python 3.10** so it requires using 3.10+

## Contributing
All comments and suggestions are appreciated, but make sure that your contribution follows basic community guidelines.

> If you are having troubles with package contact with me on <teviroff@gmail.com>, [create an issue](https://github.com/teviroff/python-trackers/issues) on GitHub, or [make a pull-request](https://github.com/teviroff/python-trackers/compare) with fix.

## Authors
* *Mikhail Kaluzhnyy* - **Creator** - [teviroff](https://github.com/teviroff)