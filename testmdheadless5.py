#!/usr/bin/env python
"""Example script accessing moneydance data in 'headless' mode using jpype
in this example we actually invoke the moneydance gui, and call up
the import capability native to the application.
This actually calls up jar files from your md installation, you need to
make sure that the appropriate files are identified below.
More information on jpype here:
https://jpype.readthedocs.io/en/latest/userguide.html
note that project jar files are from MD Preview Version
******
Copyright (c) 2021, Dale Furrow
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""
#%%
import numpy as np
import pandas as pd
from datetime import datetime, date
import os
import re
import itertools
from glob import glob
from pathlib import Path
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)
pd.options.display.float_format = '{:,.2f}'.format
#%%
import jpype
import jpype.imports
from jpype.types import *
#%%
# get oriented, print current working directory (script is based on working directory as project root)
print("Working Directory: {0}".format(os.getcwd()))
print("load all jar files from moneydance installation (change jar files directory if needed)...")
jar_files_dir = r"C:\Program Files\Moneydance\lib\*.jar"
all_jar_files = glob(jar_files_dir)

#%%
print("Launch the JVM that is found in the moneydance installation...change directory if needed")
print("Starting JVM...")
jvm_path = r"C:\Program Files\Moneydance\jre\bin\server\jvm.dll"
jpype.startJVM(classpath=all_jar_files, jvmpath=jvm_path)
#%%
# import useful classes from moneydance jar
print("Importing useful Moneydance Classes...")
from com.moneydance.apps.md.controller import AccountBookWrapper
from com.infinitekind.moneydance.model import AccountBook
from com.infinitekind.moneydance.model import Account
from com.infinitekind.moneydance.model import TxnSet
from com.infinitekind.moneydance.model import AbstractTxn
from com.infinitekind.moneydance.model import ParentTxn
from com.infinitekind.moneydance.model import SplitTxn
from com.infinitekind.moneydance.model import TxnUtil
from com.infinitekind.moneydance.model import CurrencyType
from com.infinitekind.moneydance.model import CurrencySnapshot
from com.infinitekind.moneydance.model import CurrencyTable
from com.infinitekind.moneydance.model import CurrencyUtil
from com.infinitekind.moneydance.model import MoneydanceSyncableItem
# More Useful Classes...
from com.moneydance.apps.md.controller import Main
from com.moneydance.apps.md.view.gui import MoneydanceGUI
from com.moneydance.apps.md.controller.platforms import PlatformHelper
from com.moneydance.apps.md.controller.platforms import WinHelper
from com.moneydance.apps.md.controller import UserPreferences
#%%
print("Importing useful Java Classes...")
from java.io import File
from jpype import JString
#%%
# get a config.dict file (could build one instead)
prefsFile = File(str(Path.home() / '.moneydance/config.dict'))
preferences = UserPreferences(prefsFile)
print("printing some settings from User Preferences...")
print(preferences.getSetting("backup.location"))
print(preferences.getSetting("current_accountbook"))
#%%
print("Get a windows helper")
winHelper = WinHelper()
#%%
print("initialize main...")
main = Main()
main.initializeApp(winHelper, prefsFile)
#%%
print("prove moneydance data file exists, load it into java File object")
mdTestFolder = "resources\\testMD02.moneydance"
print("Moneydance Data File exists? {0}, in {1}".format(os.path.exists(mdTestFolder), mdTestFolder))
mdFileJava = File(mdTestFolder)
#%%
print("get moneydance file, attach it to main, this will start the application gui...")
main.setInitialFile(mdFileJava)
startBook = AccountBookWrapper.wrapperForFolder(mdFileJava)
main.setCurrentBook(startBook)
#%%
print("start application...since it is reset to test file, there is a warning produced, you have to accept it...")
print("problem is, starting application shuts down other functions...")
# main.startApplication()
#%%
print("initialize a moneydance gui object")
mdGui = MoneydanceGUI(main)
#%%
print("print all the accounts, find the checking account and assign it to a variable...")
root_account = mdGui.getCurrentBook().getRootAccount()
for account in root_account.getSubAccounts():
    account_name = account.getAccountName()
    print(account_name)
    if account_name == 'Checking':
        print("found Checking Account...uuid {0}".format(account.getUUID()))
        checking_account = account


#%%
print("get path to sample qif file...")
path_to_qif_file = str(Path('./resources/sample.qif').absolute())
md_uri = "moneydance:importprompt:?file={0}".format(path_to_qif_file)
# URI Scheme: https://infinitekind.com/dev/urischeme
print("moneydance uri: {0}".format(md_uri))
#%%
print("Show import dialog...")
mdGui.showImportUI(JString(md_uri), checking_account)
#%%
# Note, could also do an "invoke and quit" command to run a python file as noted here:
# https://infinitekind.tenderapp.com/discussions/general-questions/
# 1659-command-line-arguments-where-can-i-find-the-documentation
print("alternatively, just import the file")
md_uri = "moneydance:importfile:?file={0}".format(path_to_qif_file)
mdGui.importFile(md_uri, checking_account)
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
#%%
