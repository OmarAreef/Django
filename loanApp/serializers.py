from rest_framework import serializers, validators
from .models import User, Loan, Loan_fund



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role'];
    
    extra_kwargs = {
        "password":{"write_only": True}
    }

    def create(self,validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        instance.set_password(password)
        instance.save()
        return instance

class FundSerializer(serializers.ModelSerializer):
    class Meta:
        model=Loan_fund
        fields=[ 
            "id",
            "min_amount",
            "max_amount",
            "rate", 
            "duration",
            "is_fund",
            ]

class LoanSerializer(serializers.ModelSerializer):
    fund = FundSerializer()
    class Meta:
        model=Loan
        fields=[
            "id",
            "amount",
            "fund",
            "accepted", 
            "is_fund",
            "user"
            ]