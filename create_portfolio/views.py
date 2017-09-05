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
        sp500 = Historical_Data.filter(instrument="S&P 500", date="2017-06-30")
        msci_europe = Historical_Data.filter(instrument="MSCI Europe", date="2017-06-30")
        msci_em = Historical_Data.filter(instrument="MSCI Emerging Markets", date="2017-06-30")
        bonds = Historical_Data.filter(instrument="ICE US Core Bond", date="2017-06-30")
        cash = Historical_Data.filter(instrument="Effective Federal Funds Rate", date="2017-06-30")
        gold = Historical_Data.filter(instrument="Gold Price: London Fixings, LBMA PM", date="2017-06-30")

        print(sp500.values())
        print(bonds.values())
        print(cash.values())
        print(gold.values())
        print(msci_em.values())
        print(msci_europe.values())

        # data = []
        # dates = []
        # assets = []
        #

        # for key, value in request.GET.items():
        #     if (key == "addSP500") and (value)
















        returns, cov_mat, avg_rets = optimizer.create_test_data()

        section("Example returns")
        print(returns.head(10))
        print("...")

        section("Average returns")
        print(avg_rets)

        section("Covariance matrix")
        print(cov_mat)

        # have to keep target within domain of expected returns of assets
        # else cvxopt/numpy will return domain error or convergence problem
        target_ret = avg_rets.quantile(0.7)
        weights = optimizer.markowitz_portfolio(cov_mat, avg_rets, 0.0049, allow_short=False, market_neutral=False)

        print_portfolio_info(returns, avg_rets, weights)



        content = weights.to_json()

        print(content)
        # print("req: ", request.GET.urlencode()) # get("addedGold")
        # print("type: ", type(request))

        for key, value in request.GET.items():
            # print("%s %s" % (key, value))
            print(key, value)

        return Response(content)




# daily to monthly
# https://www.packtpub.com/mapt/book/big_data_and_business_intelligence/9781787123137/15/ch15lvl1sec128/resampling-data-from-daily-to-monthly-returns


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