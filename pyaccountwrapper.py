#!/usr/bin/env python
"""
This is a python-based wrapper class for moneydance data

"""
import sys
import traceback
from pprint import pprint
#%%
import numpy as np
import pandas as pd
from pandas.tseries.offsets import Day
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
from com.moneydance.apps.md.controller import AccountBookWrapper
from com.infinitekind.moneydance.model import AccountBook
from com.infinitekind.moneydance.model import Account
from com.infinitekind.moneydance.model.Account import AccountType
from com.infinitekind.moneydance.model.AccountUtil import getBalanceAsOfDate
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
from java.io import File
from java.lang import String
from java.lang import Long
from java.lang import Integer




class PyAccountWrapper:
    _account_book: AccountBook = None
    _account: Account = None
    _id: String = None
    _name: String = None
    _type: AccountType = None
    _is_investment: bool = False
    _is_security: bool = False
    _security_account_wrappers: list = None
    date_int_fmt = '%Y%m%d'
    excluded_types = ['INCOME', 'EXPENSE']
    valid_types = ['ROOT', 'BANK', 'CREDIT_CARD', 'INVESTMENT', 'SECURITY',
                   'ASSET', 'LIABILITY','LOAN', 'EXPENSE', 'INCOME']

    def __init__(self, account_book: AccountBook, account: Account):
        self._account_book = account_book
        self._account = account
        self._id = str(account.getUUID())
        self._name = str(account.getAccountName())
        self._type = str(account.getAccountType())
        if self._type == 'INVESTMENT':
            self._is_investment = True
            self._security_account_wrappers = []
            securityAccounts = account.getSubAccounts()
            for securityAccount in securityAccounts:
                security_balance: PyAccountWrapper = PyAccountWrapper(self._account_book, securityAccount)
                security_balance.set_is_security(True)
                self._security_account_wrappers.append(security_balance)

    def set_is_security(self, is_security: bool):
        self._is_security = is_security

    def get_balance_as_of(self, close_date_int: int):
        divisor: float = 10000. if self._is_security else 100.
        return float(getBalanceAsOfDate(self._account_book, self._account, close_date_int, True)) / divisor

    def __str__(self):
        output_str = str(self._name) + ' ' + str(self._id) + " " + str(self._type) + '\n'
        if self._security_account_wrappers:
            for security_account_wrapper in self._security_account_wrappers:
                output_str = output_str + "  " + str(security_account_wrapper)
            return output_str
        else:
            return output_str

    def get_security_snapshot(self, date_int: int):
        if self._is_security:
            return self._account.getCurrencyType().getSnapshotForDate(date_int)
        else:
            return None

    def get_account_value_as_of(self, date_int: int, account_name: str, parent_account_name: str):
        balance = self.get_balance_as_of(date_int)
        price = self.get_price(date_int)
        net_worth_dict = {'date': pd.Timestamp(str(date_int)), 'parent_account': parent_account_name,
                          'account': account_name, 'balance': balance,
                          'price':price, 'total': price * balance}
        return net_worth_dict

    def get_net_worth_as_of(self, date_int: int):
        out_list = [self.get_account_value_as_of(date_int, 'CASH', self._name)]
        if self._security_account_wrappers is None or len(self._security_account_wrappers) == 0:
            return out_list
        else:
            for security_account_wrapper in self._security_account_wrappers:
                security_new_worth = security_account_wrapper\
                    .get_account_value_as_of(date_int, security_account_wrapper.get_name(), self._name)
                out_list.append(security_new_worth)
            return out_list

    def get_price(self, date_int: int):
        currency_type = self._account.getCurrencyType()
        return 1. / currency_type.getRelativeRate(date_int)

    def get_security_account_wrappers(self):
        return self._security_account_wrappers

    def get_account(self):
        return self._account

    def get_transactions(self):
        return self._account_book.getTransactionSet().getTransactionsForAccount(self._account)

    def get_name(self):
        return self._name

    @staticmethod
    def query_accounts_list(account_book: AccountBook):
        out_list = []
        root_account: Account = account_book.getRootAccount()
        for account in root_account.getSubAccounts():
            accountType: str = str(account.getAccountType())
            if accountType not in PyAccountWrapper.excluded_types:
                out_list.append(PyAccountWrapper(account_book, account))
        return out_list

def get_accounts_list_from_md_data(md_folder: str):
    print("prove moneydance data file exists, load it into java File object")

    print("Moneydance Data File exists? {0}, in {1}".format(os.path.exists(md_folder), md_folder))
    mdFileJava = File(md_folder)
    last_modded_long = mdFileJava.lastModified()  # type is java class 'JLong'
    last_modded_ts = pd.Timestamp(int(last_modded_long) / 1000, unit='s', tz='US/Central')
    print("data folder last modified: {0}".format(last_modded_ts.isoformat()))
    print("now get AccountBookWrapper, accountBook, and rootAccount")
    wrapper = AccountBookWrapper.wrapperForFolder(mdFileJava)  # wrapper is of java type 'AccountBookWrapper'
    wrapper.loadDataModel(None)
    accountBook = wrapper.getBook()
    root_account = accountBook.getRootAccount()
    print("Verify by printing useful information about these elements...")
    print("The name of the rootAccount is {0}".format(root_account.getAccountName()))
    print("The id of the rootAccount is {0}".format(root_account.getUUID()))
    txnSet = accountBook.getTransactionSet()
    transactionCount = int(txnSet.getTransactionCount())
    print("There are {0:d} transactions in the AccountBook".format(transactionCount))
    accountCount = int(root_account.getSubAccounts().size())
    print("There are {0:d} sub-accounts in the rootAccount".format(accountCount))
    return accountBook, PyAccountWrapper.query_accounts_list(accountBook)

def close_account_book(accountBook: AccountBook):
    print('closing account book: {0}'.format(str(accountBook.getRootFolder())))
    accountBook.cleanUp()



def main():
    try:
        md_folder = "resources\\testMD02.moneydance"
        account_book, account_wrappers = get_accounts_list_from_md_data(md_folder)
        for account_wrapper in account_wrappers:
            print(account_wrapper)
        account_worths = []
        for account_wrapper in account_wrappers:
            account_worths.extend(account_wrapper.get_net_worth_as_of(20090815))
        net_worth_df: pd.DataFrame = pd.DataFrame.from_records(account_worths)
        print(net_worth_df)
        close_account_book(account_book)
    except Exception as ex:
        print("Exception in user code:")
        print('-' * 60)
        print(str(ex))
        traceback.print_exc(file=sys.stdout)
        print('-' * 60)


if __name__ == '__main__':
    main()
