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
    myId = serializers.IntegerField(default=0)
    class Meta:
        model=Loan_fund
        fields=[ 
            "id",
            "min_amount",
            "max_amount",
            "rate", 
            "duration",
            "is_fund",
            "myId"
        ]

    def create(self, validated_data):
        print(validated_data)
        myfund = validated_data.pop('myId')
        #print(self.fund)
        # validated_data['fund'] = Loan.objects.filter(id = fund.fund_id)
        
        loan = Loan_fund.objects.create(**validated_data)
        return loan

class LoanSerializer(serializers.ModelSerializer):
    fund = FundSerializer( )
    class Meta:
        model=Loan
        fields=[
            "id",
            "amount",
            "fund",
            "fund_id", 
            "accepted", 
            "principal",
            "is_fund",
            "user"
            ]

    def create(self, validated_data):
        print(validated_data)
        myfund = validated_data.pop('fund')
        #print(self.fund)
        # validated_data['fund'] = Loan.objects.filter(id = fund.fund_id)
        validated_data['fund_id'] = myfund['myId']
        loan = Loan.objects.create(**validated_data)
        return loan
    