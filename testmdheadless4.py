#!/usr/bin/env python
"""Example script accessing moneydance data in 'headless' mode using jpype
Here we call up information about the moneydance file and show how to set
history
More information on jpype here:
https://jpype.readthedocs.io/en/latest/userguide.html
note that project jar files are from MD Preview Version
This file shows how to get classes from a mxt file, in this case investment reports
NOTE: The jar file here is similar to the *.mxt file in investment reports file:
https://github.com/dkfurrow/moneydance-investment-reports
The only modification is that moneydance.jar is bundled WITH investment reports classes
To do so, use the 'zipgroupfileset' command as in  buildbundled.xml
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
moneydance_jar_path = 'lib/invextension_bundled.jar'
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
print("Importing useful Investment Reports Classes...")
from com.moneydance.modules.features.invextension import ReportConfig
from com.moneydance.modules.features.invextension import BulkSecInfo
from com.moneydance.modules.features.invextension import TotalFromToReport
from com.moneydance.modules.features.invextension import TransactionValues

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
print("call up a Report Configuration object from investment reports suitable for testing")
reportConfig = ReportConfig.getTestReportConfig(root_account, False)
print("Here is that report config: \n{0}".format(reportConfig))
#%%
print("now call up a 'BulkSecInfo object from investment reports")
bulkSecInfo = BulkSecInfo(accountBook, reportConfig)

#%%
print("and list out currency price data from the 'BulkSecInfo object...")
currency_data_py = []
currencies_info_java = [x for x in bulkSecInfo.ListAllCurrenciesInfo()]
for currency_info in currencies_info_java:
    currency_data_py.append(list(ele.strip(" '[]") for ele in str(currency_info).split(',')))
header = [x.strip() for x in str(BulkSecInfo.listCurrencySnapshotHeader()).split(',')]
all_currencies_info = pd.DataFrame(data=currency_data_py, columns=header)
all_currencies_info['Date'] = all_currencies_info['Date'].astype('datetime64[ns]')
for item in ['PricebyDate', 'PriceByDate(Adjust)']:
    all_currencies_info[item] = all_currencies_info[item].astype('float')
print(all_currencies_info.iloc[:10, :].to_string(index=False))

#%%
print("and list out transaction values objects from the 'BulkSecInfo object...")
transaction_data_py = []
transaction_info_java = [x for x in bulkSecInfo.listAllTransValues()]
for transaction_info in transaction_info_java:
    transaction_data_py.append(list(ele.strip(" '[]") for ele in str(transaction_info).split(',')))
header = [x.strip() for x in str(TransactionValues.listTransValuesHeader()).split(',')]
all_transaction_info = pd.DataFrame(data=transaction_data_py, columns=header)
all_transaction_info.iloc[:, 5] = all_transaction_info.iloc[:, 5].astype('datetime64[ns]')
for ind in list(range(8,len(all_transaction_info.columns))):
    all_transaction_info.iloc[:, ind] = all_transaction_info.iloc[:, ind].astype('float')
print(all_transaction_info.iloc[:10, :].to_string(index=False))

#%%
print("now get table of currency items with last price data")
all_currencies_info.sort_values(by=['Ticker', 'Date'], inplace=True)
currency_update_df = all_currencies_info.loc[:, ['id', 'Name', 'Ticker', 'Date', 'PricebyDate']]\
    .pivot_table(index = ['id', 'Name', 'Ticker'], aggfunc='last')
currency_update_df.reset_index(inplace=True)
currency_update_df.set_index(keys = 'Ticker', inplace=True)
print(currency_update_df)
#%%
print("So let's take a look at Citigroup, and update the price...")
new_price_info = ('C', 20100607, 3.64)
print("For ticker {0} on dateInt {1:d} we want to assign a price of {2:.2f}".format(*new_price_info))

#%%
uuid = currency_update_df[currency_update_df.index == new_price_info[0]].loc[new_price_info[0], 'id']
print('UUID for {0} is {1}'.format(new_price_info[0], uuid))
#%%
currencyType = accountBook.getCurrencyByUUID(uuid)
currencySnapshot = currencyType.addSnapshotInt(new_price_info[1], 1 / new_price_info[2])
print("Syncing AccountBook...")
syncSuccess = currencySnapshot.syncItem()
print("SyncSuccess? {0}".format(syncSuccess))
isSaved = accountBook.save()
print("AccountBook Saved? {0}".format(isSaved))
#%%
new_rate = currencyType.getRateByDate(new_price_info[1], None)
print("Confirm New Price of {0:.2f} for {1:d}".format(1. / new_rate, new_price_info[1]))
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
