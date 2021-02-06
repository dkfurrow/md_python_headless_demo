#!/usr/bin/env python
"""Example script accessing moneydance data in 'headless' mode using jpype
More information on jpype here:
https://jpype.readthedocs.io/en/latest/userguide.html
note that project jar files are from MD Preview Version
This file shows how to get classes from a mxt file, in this case investment reports
NOTE: The jar file here is similar to the *.mxt file in investment reports file:
https://github.com/dkfurrow/moneydance-investment-reports
The only modification is that moneydance.jar is bundled WITH investment reports classes
To do so, use the 'zipgroupfileset' command as in  buildbundled.xml
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
from com.moneydance.modules.features.invextension import Prefs
from com.moneydance.modules.features.invextension import DateRange
from com.moneydance.modules.features.invextension import TotalFromToReport
from com.moneydance.modules.features.invextension import TotalSnapshotReport
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
dateRange = DateRange(20090601, 20100601, 20100601)
reportConfig.setUseAverageCostBasis(True)
reportConfig.setDateRange(dateRange)
print("Here is that report config: \n{0}".format(reportConfig))
bulkSecInfo = BulkSecInfo(accountBook, reportConfig)
#%%
print("now call up a 'a displayed report from investment reports")
fromToReport = TotalFromToReport(reportConfig, bulkSecInfo)
fromToReport.calcReport()
fromToReport.displayReport()
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
