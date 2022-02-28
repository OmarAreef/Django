from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    email = models.CharField(max_length=255, null=True, blank=True);
    password = models.CharField(max_length=100);
    role = models.CharField(max_length=100, default="customer");
    username = models.CharField(max_length=100, unique=True);

    REQUIRED_FIELD = [
        "username",
        "role",
        "password"
    ]

class Loan_fund(models.Model):
    
    min_amount = models.IntegerField(default=0 ,);
    max_amount = models.IntegerField();
    rate = models.DecimalField(max_digits=3, decimal_places=1 ,);
    duration = models.IntegerField();
    is_fund = models.BooleanField(default=False ,) ;

    REQUIRED_FIELD = [
            "min_amount",
            "max_amount",
            "rate", 
            "duration",
            "is_fund",
            
        ]

class Loan(models.Model):
    amount = models.IntegerField();
    accepted = models.BooleanField( default = False);
    user = models.ForeignKey(User, on_delete=models.CASCADE,);
    is_fund = models.BooleanField();
    fund = models.ForeignKey(Loan_fund, on_delete=models.CASCADE,);

    REQUIRED_FIELD = [
            "amount",
            "fund",
            "accepted", 
            "is_fund",
            "user"
    ]
