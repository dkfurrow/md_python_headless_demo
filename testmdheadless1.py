#!/usr/bin/env python
"""Example script accessing moneydance data in 'headless' mode using jpype
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
#%%
# Launch the JVM
moneydance_jar_path = 'lib/moneydance.jar'
print("Moneydance Jar File exists? {0}, in {1}".format(os.path.exists(moneydance_jar_path), moneydance_jar_path))
print("Starting JVM...")
jpype.startJVM(classpath=[moneydance_jar_path])
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
#%%
print("Importing useful Java Classes...")
from java.io import File
#%%
print("prove moneydance data file exists, load it into java File object")
mdTestFolder = "resources\\testMD02.moneydance"
print("Moneydance Data File exists? {0}, in {1}".format(os.path.exists(mdTestFolder), mdTestFolder))
mdFileJava = File(mdTestFolder)
last_modded_long = mdFileJava.lastModified()  # type is java class 'JLong'
last_modded_ts = pd.Timestamp(int(last_modded_long) / 1000, unit='s', tz='US/Central')
print("data folder last modified: {0}".format(last_modded_ts.isoformat()))
#%%
print("now get AccountBookWrapper, accountBook, and rootAccount")
wrapper = AccountBookWrapper.wrapperForFolder(mdFileJava)  # wrapper is of java type 'AccountBookWrapper'
wrapper.loadDataModel(None)
accountBook = wrapper.getBook()
root_account = accountBook.getRootAccount()
#%%
print("Verify by printing useful information about these elements...")
print("The name of the rootAccount is {0}".format(root_account.getAccountName()))
print("The id of the rootAccount is {0}".format(root_account.getUUID()))
txnSet = accountBook.getTransactionSet()
transactionCount = int(txnSet.getTransactionCount())
print("There are {0:d} transactions in the AccountBook".format(transactionCount))
accountCount = int(root_account.getSubAccounts().size())
print("There are {0:d} sub-accounts in the rootAccount".format(accountCount))
#%%
print("printing details on last 10 parent transactions...")
parent_txns = [x for x in txnSet.iterableTxns() if isinstance(x, ParentTxn)]
for txn in parent_txns:
    print("transaction date {0:d} account {1} description: {2} for amount {3}"
          .format(int(txn.getDateInt()), txn.getAccount().getAccountName(), txn.getDescription(),
                  txn.getAccount().getCurrencyType().formatFancy(txn.getValue(), '.')))

#%%
print("Printing Information on Securities...")
from com.infinitekind.moneydance.model.CurrencyType import CURRTYPE_SECURITY
currencies = accountBook.getCurrencies().getAllCurrencies()
securities = [x for x in currencies if x.getCurrencyType() == CurrencyType.Type.SECURITY]

for security in securities:
    last_snapshot = [x for x in security.getSnapshots()][-1]
    price = 1 / float(last_snapshot.getRate())
    dateInt = last_snapshot.getDateInt()
    ticker = security.getTickerSymbol()
    print("Name: {0} Ticker:{1} last snapshot: {2:d} last price {3:.3f}"
          .format(security.getName(), ticker ,dateInt, price))

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
#%%
#%%
#%%
#%%
