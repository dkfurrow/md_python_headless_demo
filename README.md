# Moneydance Headless Python Demo

This is a demonstration of how to access a [moneydance](https://infinitekind.com/moneydance) datafile via python using the [JPype](https://jpype.readthedocs.io/en/latest/) package. The example scripts shown herein demonstrate how to access a moneydance datafile (a sample included in this repo), how to run the [investment reports](https://github.com/dkfurrow/moneydance-investment-reports) extension from python, (two different ways) and how to update the price of a security in the datafile. The motivation for this is simple--moneydance has the ability to run python scripts in the application, but you may want to access the data as part of a larger python program, or you may want to take advantage of specific ipython features or the ability to run a script in a regular python environment, and this demo shows you how.  As always, **please backup** your data before attempting any external query or setting of any data element, and please note that the use of any scripts contained in this repo is *at your own risk*. 

### Update: August 2022
In these scripts we test against a moneydance data set which is **not** password protected.  If you need to unlock a password-protected data set, please see [Stuart Beesley's](https://yogi1967.github.io/MoneydancePythonScripts/) collection of scripts for instruction on how to manage the password issue, and also see [the discussion on moneydance forums here.](https://infinitekind.tenderapp.com/discussions/moneydance-development/4719-headless-access-for-moneydance-data-in-python-demonstration-and-code).

Additionally, I wrote a more fulsome `PyAccountWrapper` class in `pyaccountwrapper.py` to handle account queries, most notably to get account balances and prices and specific dates.  The demonstrion of this class is in the script `testmdheadless_net_worth.py`.

## Getting Started

You'll need a python installation of some kind that includes [pandas](https://pandas.pydata.org/) and [JPype](https://jpype.readthedocs.io/en/latest/).  For windows I prefer [Winpython](https://winpython.github.io/) as it's easy to use and contains pandas in the distribution. You'll need a JDK that is compatible with moneydance (the repo contains the latest preview build jar of moneydance [2021.1 (3034) as of this writing].  [OpenJDK](https://jdk.java.net/15/) worked for me, and is consistent with the java package bundled with moneydance.  Version as of this writing is openjdk 15.0.2 2021-01-19. 

### Demonstration Video
If you want to see how this should look when you run it, I have made [this desktop video](https://vimeo.com/509314311) to demonstrate.

### Prerequisites

It's not strictly necessary to run these scripts, but it's helpful to have a decent IDE, my favorite is [Pycharm](https://www.jetbrains.com/pycharm/features/), especially when you use the [cell mode](https://plugins.jetbrains.com/plugin/7858-pycharm-cell-mode) plugin.  

## Running the scripts
The scripts are basically self-explanatory.  A sample moneydance file and all necessary jars are included in the repo.


## Author

* **Dale Furrow** - [Dale's Github](https://github.com/dkfurrow/)


## License

This project is licensed under the BSD License - see the [Open Source Initiative](https://opensource.org/licenses/BSD-3-Clause) file for details

## Acknowledgments

* Thanks to Sean Reilly at Moneydance for numerous tips and encouragements

