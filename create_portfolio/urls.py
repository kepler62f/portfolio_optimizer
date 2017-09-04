from django.conf.urls import url
from create_portfolio.views import OptimizerView

# We are adding a URL called /home
urlpatterns = [
    url(r'^get_optimal_weights/', OptimizerView.as_view()),
]

# name='get_optimal_weights'