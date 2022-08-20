#!/usr/bin/env python
"""MD Fetch Module


"""
import sys
import os
import traceback
from random import randint
from collections import OrderedDict
from pathlib import Path
import pandas as pd
from pandas.tseries.offsets import BDay
from pandas.tseries.offsets import DateOffset
import re
#
import jpype.imports
#
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 200)
pd.options.display.float_format = '{:,.2f}'.format

MODULE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class MDFetcher(object):
    valid_ticker_match=r"^(NoTicker|.+NDQ|CASH)$"
    _md_bundled_jar_location: str = None
    _md_file_location: str = None
    _wrapper = None
    _accountBook = None
    _rootAccount = None
    _reportConfig = None
    _bulkSecInfo = None
    _snapshotReport: pd.DataFrame = None
    _netPositions: pd.DataFrame = None
    _all_currencies_data: pd.DataFrame = None
    _latest_currency_prices: pd.DataFrame = None

    def __init__(self, md_bundled_jar_location: str,  md_file_location: str):
        self._md_bundled_jar_location = md_bundled_jar_location
        self._md_file_location = md_file_location
        self.init_md_jar()
        self.load_md_file()

    def init_md_jar(self):
        jpype.startJVM(classpath=[str(Path(self._md_bundled_jar_location).absolute())])

    def load_md_file(self):
        if Path(self._md_file_location).absolute().exists():
            from java.io import File
            mdFileJava = File(self._md_file_location)
            last_modded_long = mdFileJava.lastModified()  # type is java class 'JLong'
            last_modded_ts = pd.Timestamp(int(last_modded_long) / 1000, unit='s', tz='US/Central')
            print("data folder last modified: {0}".format(last_modded_ts.isoformat()))
            print("now get AccountBookWrapper, accountBook, and rootAccount")
            # wrapper is of java type 'AccountBookWrapper'
            from com.moneydance.apps.md.controller import AccountBookWrapper
            self._wrapper = AccountBookWrapper.wrapperForFolder(mdFileJava)
            self._wrapper.loadDataModel(None)
            self._accountBook = self._wrapper.getBook()
            self._root_account = self._accountBook.getRootAccount()

    def close_md_file(self):
        self._accountBook.cleanUp()
        self._accountBook = None
        self._wrapper = None
        self._root_account = None
        self._reportConfig = None
        self._bulkSecInfo = None
        print("Moneydance file closed...")

    def load_BulkSecInfo(self, last_bday: pd.Timestamp = pd.Timestamp.now().normalize() - BDay(1)):
        print("fetching Bulk Security Info...")
        from com.moneydance.modules.features.invextension import ReportConfig
        from com.moneydance.modules.features.invextension import AggregationController  # enum INVACCT, TICKER, SECTYPE
        from com.moneydance.modules.features.invextension import BulkSecInfo
        from com.moneydance.modules.features.invextension import DateRange
        year_ago_dt = last_bday - DateOffset(months=12) if BDay().is_on_offset(last_bday - DateOffset(months=12)) \
            else last_bday - DateOffset(months=12) - BDay(1)
        self._reportConfig = ReportConfig.getTestReportConfig(self._root_account, False, AggregationController.INVACCT)
        dateInt_format = '%Y%m%d'
        dateRange = DateRange(int(year_ago_dt.strftime(dateInt_format)), int(last_bday.strftime(dateInt_format)),
                              int(last_bday.strftime(dateInt_format)))
        self._reportConfig.setUseAverageCostBasis(True)
        self._reportConfig.setOutputSingle(True)
        self._reportConfig.setDateRange(dateRange)
        self._bulkSecInfo = BulkSecInfo(self._accountBook, self._reportConfig)

    def calc_snap_report(self, remove_aggregates=True):
        print("Fetching snapshot report...")
        from com.moneydance.modules.features.invextension import BulkSecInfo
        from com.moneydance.modules.features.invextension import TotalSnapshotReport
        from com.moneydance.modules.features.invextension import InvestmentAccountWrapper
        from com.moneydance.modules.features.invextension import SecurityAccountWrapper
        from com.moneydance.modules.features.invextension import SecurityTypeWrapper
        from com.moneydance.modules.features.invextension import SecuritySubTypeWrapper
        from com.moneydance.modules.features.invextension import CurrencyWrapper
        from com.moneydance.modules.features.invextension.SecurityReport import MetricEntry

        def get_display_val(obj):
            if any([isinstance(obj, InvestmentAccountWrapper),
                    isinstance(obj, SecurityAccountWrapper),
                    isinstance(obj, SecurityTypeWrapper),
                    isinstance(obj, SecuritySubTypeWrapper),
                    isinstance(obj, CurrencyWrapper)]):
                return str(obj.getName())
            elif isinstance(obj, MetricEntry):
                return obj.getDisplayValue() if obj.getDisplayValue() < sys.float_info.max else float('nan')
            else:
                return None
        snapshotReport = TotalSnapshotReport(self._reportConfig, self._bulkSecInfo)
        snapshotReport.calcReport()
        snapObj = snapshotReport.getReportTable()
        header = [str(col) for col in snapshotReport.getModelHeader()]
        header = [col.replace('\n', ' ') for col in header]
        print("here's the header...")
        print(header)
        all_data = []
        for row in snapObj:
            row_data = {}
            for i, ele in enumerate(row):
                row_data[header[i]] = get_display_val(ele)
            all_data.append(row_data)
        self._snapshotReport = pd.DataFrame(all_data)
        if remove_aggregates:
            self._snapshotReport = self._snapshotReport[self._snapshotReport['SecType'].str.len() > 0]
        print("Snapshot report fetched with {0:d} total rows...")

    def derive_net_positions(self):
        df = self._snapshotReport[self._snapshotReport['End Pos'] > 0.].copy()
        agg_cols = OrderedDict(
            [('Security', 'last'), ('SecType', 'last'), ('SecSubType', 'last'), ('Last Price', 'last'),
             ('End Pos', 'sum'), ('End Value', 'sum'), ('Abs PrcChg', 'last'), ('Abs ValChg', 'sum'),
             ('Pct PrcChg', 'last'), ('Long Basis', 'sum'), ('Short Basis', 'sum'), ('Income', 'sum'),
             ('Rlzd Gain', 'sum'), ('Unrlzd Gain', 'sum'), ('Total Gain', 'sum')])
        self._netPositions = df.pivot_table(index='Ticker', aggfunc=agg_cols)[agg_cols.keys()]

    def get_net_positions(self):
        return self._netPositions

    def extract_all_currency_data(self):
        from com.moneydance.modules.features.invextension import BulkSecInfo
        currency_data_py = []
        currencies_info_java = [x for x in self._bulkSecInfo.ListAllCurrenciesInfo()]
        for currency_info in currencies_info_java:
            currency_data_py.append(list(ele.strip(" '[]") for ele in str(currency_info).split(',')))
        header = [x.strip() for x in str(BulkSecInfo.listCurrencySnapshotHeader()).split(',')]
        self._all_currencies_data = pd.DataFrame(data=currency_data_py, columns=header)
        self._all_currencies_data['Date'] = self._all_currencies_data['Date'].astype('datetime64[ns]')
        for item in ['PricebyDate', 'PriceByDate(Adjust)']:
            self._all_currencies_data[item] = self._all_currencies_data[item].astype('float')

    def filter_latest_currency_prices(self, current_positions=True):
        valid_call = (self._all_currencies_data is not None) and \
                     (self._netPositions is not None if current_positions else True)
        if valid_call:
            all_tickers = [x for x in self._all_currencies_data['Ticker'].unique() if
                           not re.match(self.valid_ticker_match, x)]
            current_tickers = [x for x in self._netPositions.index.unique() if
                           not re.match(self.valid_ticker_match, x)]
            self._all_currencies_data.sort_values(by=['Ticker', 'Date'], inplace=True)
            self._latest_currency_prices: pd.DataFrame = self._all_currencies_data[self._all_currencies_data['Ticker']
                .isin(current_tickers if current_positions else all_tickers)] \
                .loc[:, ['id', 'Name', 'Ticker', 'Date', 'PricebyDate']]\
                .pivot_table(index=['id', 'Name', 'Ticker'], aggfunc='last')
            self._latest_currency_prices.reset_index(inplace=True)
            self._latest_currency_prices.set_index(keys='Ticker', inplace=True)
            self._latest_currency_prices.sort_index(inplace=True)
        else:
            raise ValueError("call to filter latest currency invalid--check whether precedents are met!")

    def get_all_currency_data(self):
        return self._all_currencies_data

    def get_latest_currency_prices(self):
        return self._latest_currency_prices

def main():
    try:
        mdTestFolder = str(Path(r"C:\Users\dalef\.moneydance\Documents\FurrowCurrent.moneydance").absolute())
        moneydance_jar_path = str(Path(MODULE_DIRECTORY, './lib/invextension_bundled.jar').absolute())
        md_fetcher = MDFetcher(md_bundled_jar_location=moneydance_jar_path, md_file_location=mdTestFolder)
        md_fetcher.load_BulkSecInfo()
        md_fetcher.calc_snap_report()
        md_fetcher.derive_net_positions()
        print("Here are net positions...")
        print(md_fetcher.get_net_positions())
        print("query currencies...")
        md_fetcher.extract_all_currency_data()
        print(md_fetcher.get_all_currency_data().head())
        print("filter last prices...")
        md_fetcher.filter_latest_currency_prices()
        print(md_fetcher.get_latest_currency_prices())
        md_fetcher.close_md_file()

        # print Cheese(num_holes=101)
    except Exception as ex:
        print("Exception in user code:")
        print('-' * 60)
        print(str(ex))
        traceback.print_exc(file=sys.stdout)
        print('-' * 60)


if __name__ == '__main__':
    main()
