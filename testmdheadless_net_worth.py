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
from pandas.tseries.offsets import Day
from datetime import datetime, date
import os
import re
import itertools

from pyaccountwrapper import PyAccountWrapper, get_accounts_list_from_md_data, close_account_book

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)
pd.options.display.float_format = '{:,.4f}'.format

#%%
# test PyAccountWrapper using included test data
mdTestFolder = "resources\\testMD02.moneydance"
# %%
account_book, account_wrappers = get_accounts_list_from_md_data(mdTestFolder)
for account_wrapper in account_wrappers:
    print(account_wrapper)

# %%
check_dates = [20090824, 20100328]
print("generate net worth calculations for dates {0}".format(', '.join([str(x) for x in check_dates])))
account_worths = []
for account_wrapper in account_wrappers:
    for check_date in check_dates:
        account_worths.extend(account_wrapper.get_net_worth_as_of(check_date))
net_worth_df: pd.DataFrame = pd.DataFrame.from_records(account_worths)
print(net_worth_df)
# %%
close_account_book(account_book)

# %%
print(net_worth_df[(net_worth_df.date == '2009-08-24') & (net_worth_df.total != 0.)])
#%%
print(net_worth_df[(net_worth_df.date == str(20100328)) & (net_worth_df.total != 0.)])
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
