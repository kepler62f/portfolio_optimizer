# from django.shortcuts import render
# from django.http import HttpResponse

from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from create_portfolio.models import InstrumentsData

import numpy as np
import pandas as pd
import portfolioopt as optimizer

class OptimizerView(APIView):
    """
    An API endpoint for creating portfolios
    """
    def get(self, request, format=None):

        Historical_Data = InstrumentsData.objects

        # print first item

        # print(historical_data.values()[0])

        # get from DB table and store into individual asset queryset
        cash = Historical_Data.filter(instrument="Effective Federal Funds Rate").values("date", "instrument_value")
        sp500 = Historical_Data.filter(instrument="S&P 500").values("date", "instrument_value")
        msci_europe = Historical_Data.filter(instrument="MSCI Europe").values("date", "instrument_value")
        msci_em = Historical_Data.filter(instrument="MSCI Emerging Markets").values("date", "instrument_value")
        bonds = Historical_Data.filter(instrument="ICE US Core Bond").values("date", "instrument_value")
        gold = Historical_Data.filter(instrument="Gold Price: London Fixings, LBMA PM").values("date", "instrument_value")

        # print(sp500.values())
        # print(bonds.values())
        # print(cash.values())
        # print(gold.values())
        # print(msci_em.values())
        # print(msci_europe.values())

        # convert queryset into pandas dataframes
        cash_df = pd.DataFrame.from_records(cash)
        sp500_df = pd.DataFrame.from_records(sp500)
        msci_europe_df = pd.DataFrame.from_records(msci_europe)
        msci_em_df = pd.DataFrame.from_records(msci_em)
        bonds_df = pd.DataFrame.from_records(bonds)
        gold_df = pd.DataFrame.from_records(gold)

        # set date as dataframe index
        cash_ts = cash_df.set_index("date")
        sp500_ts = sp500_df.set_index("date")
        europe_ts = msci_europe_df.set_index("date")
        em_ts = msci_em_df.set_index("date")
        bonds_ts = bonds_df.set_index("date")
        gold_ts = gold_df.set_index("date")


        cash_ts.columns = ["Cash"]
        sp500_ts.columns = ["S&P 500"]
        europe_ts.columns = ["MSCI Europe"]
        em_ts.columns = ["MSCI Emerging Markets"]
        bonds_ts.columns = ["ICE US Core Bond"]
        gold_ts.columns = ["Gold"]

        # resample daily time series as monthly
        # fill NA holes with next valid observation

        mth_cash_ts = cash_ts.asfreq('M').fillna(method="backfill")
        mth_sp500_ts = sp500_ts.asfreq('M').fillna(method="backfill")
        mth_europe_ts = europe_ts.asfreq('M').fillna(method="backfill")
        mth_em_ts = em_ts.asfreq('M').fillna(method="backfill")
        mth_bonds_ts = bonds_ts.asfreq('M').fillna(method="backfill")
        mth_gold_ts = gold_ts.asfreq('M').fillna(method="backfill")

        # filter into 5-year (60-mth) monthly return series ending Jun 30, 2017
        cash_returns = mth_cash_ts["2012-06-30":"2017-06-30"]
        cash_returns.drop(cash_returns.index[0], inplace=True)
        sp500_returns = mth_sp500_ts["2012-06-30":"2017-06-30"].pct_change()
        sp500_returns.drop(sp500_returns.index[0], inplace=True)
        europe_returns = mth_europe_ts["2012-06-30":"2017-06-30"].pct_change()
        europe_returns.drop(europe_returns.index[0], inplace=True)
        em_returns = mth_em_ts["2012-06-30":"2017-06-30"].pct_change()
        em_returns.drop(em_returns.index[0], inplace=True)
        bonds_returns = mth_bonds_ts["2012-06-30":"2017-06-30"].pct_change()
        bonds_returns.drop(bonds_returns.index[0], inplace=True)
        gold_returns = mth_gold_ts["2012-06-30":"2017-06-30"].pct_change()
        gold_returns.drop(gold_returns.index[0], inplace=True)

        frames = []

        # print(cash_returns)
        # print(cash_returns.loc['instrument_value'])

        # data.append(cash_returns.loc["instrument_value"])
        # data.append(sp500_returns.loc["instrument_value"])
        # print(data)

        # merge = pd.concat([cash_returns, gold_returns], axis=1)
        # print(merge)

        assets = []
        dates = pd.date_range('7/1/2012', periods=60, freq='M', tz='UTC')
        # print(dates)

        for key, value in request.GET.items():
            if (key == "addedCash") and (value == "true"):
                # assets.append("Cash")
                # print(assets)
                frames.append(cash_returns)
            if (key == "addedSP500") and (value == "true"):
                # assets.append("S&P 500")
                # print(assets)
                frames.append(sp500_returns)
            if (key == "addedEurope") and (value == "true"):
                # assets.append("Europe")
                # print(assets)
                frames.append(europe_returns)
            if (key == "addedEM") and (value == "true"):
                # assets.append("MSCI Emerging Markets")
                # print(assets)
                frames.append(em_returns)
            if (key == "addedBonds") and (value == "true"):
                # assets.append("Bonds")
                # print(assets)
                frames.append(bonds_returns)
            if (key == "addedGold") and (value == "true"):
                # assets.append("Gold")
                # print(assets)
                frames.append(gold_returns)

        if (len(frames) > 0):
            returns = pd.concat(frames, axis=1)
            print(returns)



        # avg_rets = returns.mean()
        # cov_mat = returns.cov()












        returns, cov_mat, avg_rets = optimizer.create_test_data()

        # section("Example returns")
        # print(returns.head(10))
        # print("...")
        #
        # section("Average returns")
        # print(avg_rets)
        #
        # section("Covariance matrix")
        # print(cov_mat)

        # have to keep target within domain of expected returns of assets
        # else cvxopt/numpy will return domain error or convergence problem
        target_ret = avg_rets.quantile(0.7)
        weights = optimizer.markowitz_portfolio(cov_mat, avg_rets, 0.0049, allow_short=False, market_neutral=False)

        # print_portfolio_info(returns, avg_rets, weights)



        content = weights.to_json()

        # print(content)
        # print("req: ", request.GET.urlencode()) # get("addedGold")
        # print("type: ", type(request))

        # for key, value in request.GET.items():
            # print("%s %s" % (key, value))
            # print(key, value)

        return Response(content)





##################################
### Auxiliary Functions
##################################

def section(caption):
    print('\n\n' + str(caption))
    print('-' * len(caption))

def print_portfolio_info(returns, avg_rets, weights):
    """
    Print information on expected portfolio performance.
    """
    ret = (weights * avg_rets).sum()
    std = (weights * returns).sum(1).std()
    sharpe = ret / std
    print("Optimal weights:\n{}\n".format(weights))
    print("Expected return:   {}".format(ret))
    print("Expected variance: {}".format(std**2))
    print("Expected Sharpe:   {}".format(sharpe))