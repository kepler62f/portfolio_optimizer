from django.shortcuts import render
# from django.http import HttpResponse

import numpy as np
import pandas as pd
import portfolioopt as optimizer


def index(request):

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


    context = {
        'avg_rets': avg_rets,
        'cov_mat': cov_mat,
        'weights': weights
    }

    return render(request, 'create_portfolio/base.html', context)




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