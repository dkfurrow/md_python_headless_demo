#!/usr/bin/env python
"""Example script accessing moneydance data in 'headless' mode using jpype
Here we insert an expense transaction into a checking account
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
from pprint import pprint
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
from com.infinitekind.moneydance.model.Account import AccountType
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
from java.lang import String
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
print("printing details on parent transactions...")
parent_txns = [x for x in txnSet.iterableTxns() if isinstance(x, ParentTxn)]
for txn in parent_txns:
    print("transaction date {0:d} account {1} description: {2} for amount {3}"
          .format(int(txn.getDateInt()), txn.getAccount().getAccountName(), txn.getDescription(),
                  txn.getAccount().getCurrencyType().formatFancy(txn.getValue(), '.')))

#%%
accountInfos = []
print("Printing Information on Accounts...")
cols = ['name', 'id', 'type', 'inactive']
for account in root_account.getSubAccounts():
    accountInfos.append((str(account.getAccountName()), str(account.getUUID()),
                         str(account.getAccountType().name()),
                         str(account.getAccountIsInactive())))
account_df = pd.DataFrame(data=accountInfos, columns=cols)
print(account_df)
#%%
# print account type and values
print("Here we print out available account types, and their associated codes")
for accountType in Account.AccountType.values():
    print(accountType, accountType.code())
#%%
print("Here we identify a bank account and category for the transaction we wish to insert")
test_acct_name = account_df[account_df['type'] == 'BANK'].iloc[0, 0]
print("fetch account {0}".format(test_acct_name))
test_account = root_account.getAccountByName(test_acct_name)
test_category = root_account.getAccountByName("Personal")
print("verifying acount: {0}, {1}".format(test_account.getAccountName(), test_account.getUUID()))
print("verifying category: {0}, {1}".format(test_category.getAccountName(), test_category.getUUID()))
#%%
print("Here we create description, memo, amount and effective date for our transaction")
desc="test transaction entry from headless python connection"
memo="memo for test transaction from headless python connection"
amt = 6502 # i.e. $65.02
effectiveDateInt = 20220210
print("So we are inputting the transaction '{0}' for amount {1:.2f} for date {2:d}"
      .format(desc, float(amt/100.), effectiveDateInt))
#%%
print("Here we form the parent transaction, split, and print out the result...")
ptxn = ParentTxn(accountBook)
ptxn.setDateInt(effectiveDateInt)
ptxn.setTaxDateInt(effectiveDateInt)
ptxn.setAccount(test_account)  # parent account?
ptxn.setDescription(desc)
ptxn.setMemo(memo)
ptxn.setStatus(AbstractTxn.STATUS_RECONCILING)
s1 = SplitTxn(ptxn)
s1.setAccount(test_category)
s1.setAmount(amt, 0.0, -amt)
s1.setDescription(memo)
ptxn.addSplit(s1)
print("Here is the resultant transaction before entry into database:\n{0}".format(ptxn))
print("Balance of account '{0}' before entry of transaction: {1:.2f}"
      .format(test_account.getAccountName(), float(test_account.getBalance()/100.)))
# root_account.getTransactionSet().addNewTxn(new_txn)
#%%
print("Syncing AccountBook...")
syncSuccess = ptxn.syncItem()
print("SyncSuccess? {0}".format(syncSuccess))
isSaved = accountBook.save()
print("AccountBook Saved? {0}".format(isSaved))
print("Here is the resultant transaction after entry into database:\n{0}".format(ptxn))
print("Balance of account '{0}' after entry of transaction: {1:.2f}"
      .format(test_account.getAccountName(), float(test_account.getBalance()/100.)))
# note that 'dirty' annotations are no longer present
#%%
accountBook.cleanUp()
accountBook = None
wrapper = None
root_account = None
print("finished...")
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
