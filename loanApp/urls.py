from cmath import log
from django.urls import path;
from . import views;


# URLConf
urlpatterns = [
    path('register/' , views.Register),
    path('login/' , views.Login ),
    path('logout/' , views.Logout ),
    path('fund/', views.create_fund),
    path('getfund/', views.get_fund),
    path('loan/', views.loan_api),
    path('accept/',views.accept_loan ),
    path('pay/',views.pay_loan),
    path('reports/',views.generate_reports),
]