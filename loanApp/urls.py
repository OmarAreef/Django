from cmath import log
from django.urls import path;
from . import views;


# URLConf
urlpatterns = [
    path('register/' , views.Register),
    path('login/' , views.Login ),
    path('logout/' , views.Logout ),
    path('fund/', views.create_fund),
    path('loan/', views.loan_api),
    path('accept/',views.accept_loan ),
]