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

    context = {
        'avg_rets': avg_rets
    }

    return render(request, 'create_portfolio/base.html', context)



def section(caption):
    print('\n\n' + str(caption))
    print('-' * len(caption))

