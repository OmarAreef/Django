from django.shortcuts import render
from rest_framework import status 
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from .models import User, Loan, Loan_fund
from .serializers import UserSerializer, FundSerializer, LoanSerializer 
import jwt, datetime
from django.db.models import Sum, Q
import math



# Create your views here.

@api_view(['POST'])
@parser_classes([JSONParser])
def Register(request):
    data = request.data;
    if (data.get('role') not in ['customer', 'provider']):
        return Response({
                     "message":"Not valid role"}, status=status.HTTP_406_NOT_ACCEPTABLE);   
    
    serializer = UserSerializer(data = data);
    serializer.is_valid(raise_exception=True)
    serializer.save();
    return Response({
            "data":serializer.data,
            }, status=status.HTTP_201_CREATED)

   
    

@api_view(['POST'])
@parser_classes([JSONParser])
def Login(request):
    try :
        data= request.data;  
        user_found = User.objects.get(username=data.get('username'))
        if (user_found.check_password(data.get('password'))):
            payload = {
                "id":user_found.id,
            }
            response= Response();
            token = jwt.encode(payload, 'secret', algorithm= 'HS256').decode('utf-8')
            response.set_cookie(key='jwt', value=token, httponly=True);
            response.data = {
                    "token":token,
                }
            response.status = status.HTTP_202_ACCEPTED
            return response
        else:
            return Response(
                "password Incorrect", status=status.HTTP_400_BAD_REQUEST)       
        
    except User.DoesNotExist:
            return Response({
                     "message":"Username not found register instead"}, status=status.HTTP_400_BAD_REQUEST)

  
@api_view(['POST'])
@parser_classes([JSONParser])
def Logout(request):
    response= Response()
    response.delete_cookie('jwt')
    response.data = {"message":"success"}
    return response

@api_view(['POST'])
@parser_classes([JSONParser])
def create_fund(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return Response({
                     "message":"Not Logged in please login first"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        payload = jwt.decode(token, 'secret', algorithm=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({
                     "message":"Not Logged in please login first"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(id=payload['id']).first();
    if ( user.role == 'bank'):
        serializer = FundSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "data":serializer.data,
            }, status=status.HTTP_201_CREATED)
    return Response({
            "message":"user not authorised to create a loan fund",
            }, status=status.HTTP_400_BAD_REQUEST)


def view_loans(request):
    data = request.data
    token = request.COOKIES.get('jwt')
    if not token:
        return Response({
                     "message":"Not Logged in please login first"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        payload = jwt.decode(token, 'secret', algorithm=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({
                     "message":"Not Logged in please login first"}, status=status.HTTP_400_BAD_REQUEST)
    loans = Loan.objects.filter(user = payload['id'])
    serializer = LoanSerializer(loans, many=True)
    return Response({"data": serializer.data})

@api_view(['POST' , 'GET'])
@parser_classes([JSONParser])
def loan_api(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return Response({
                    "message":"Not Logged in please login first"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        payload = jwt.decode(token, 'secret', algorithm=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({
                    "message":"Not Logged in please login first"}, status=status.HTTP_400_BAD_REQUEST)

    if(request.method == 'POST'):
        user = User.objects.filter(id=payload['id']).first();
        loan_fund = Loan_fund.objects.filter(id = request.data['fund']).first();
        if (user != None and user.role != 'bank'):
            is_fund = False if user.role == 'customer' else True
            if (is_fund != loan_fund.is_fund):
                return Response({
                "message":"this loan cannot be created",
                }, status=status.HTTP_400_BAD_REQUEST)
            if(request.data['amount'] < loan_fund.min_amount or request.data['amount'] > loan_fund.max_amount):
                return Response({
                "message":"this loan cannot be created",
                }, status=status.HTTP_400_BAD_REQUEST)
            # 

            data = request.data
            result = data['amount'] * math.pow((1 + loan_fund.rate / 100), loan_fund.duration)
            data['amount']= result
            data['is_fund'] = is_fund
            data['user'] =  payload['id']
            serializer = LoanSerializer(data = data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "data":serializer.data,
                }, status=status.HTTP_201_CREATED)
        return Response({
                "message":"user not authorised to create a loan",
                }, status=status.HTTP_400_BAD_REQUEST)

    if(request.method == "GET"):
        return view_loans(request);


@api_view(['POST'])
@parser_classes([JSONParser])
def accept_loan(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return Response({
                     "message":"Not Logged in please login first"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        payload = jwt.decode(token, 'secret', algorithm=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({
                     "message":"Not Logged in please login first"}, status=status.HTTP_400_BAD_REQUEST)
    
    loan = Loan.objects.filter(id = request.data['id']).first()
    is_fund = loan.is_fund
    user = User.objects.filter(id=payload['id']).first()
    if (user.role == 'bank'):
        if (is_fund == False):
            all_funds = Loan.objects.filter(Q(accepted = True) & Q(is_fund = True)).aggregate(Sum('amount'))['amount__sum']
            all_loans = Loan.objects.filter(Q(accepted = True) & Q(is_fund = False)).aggregate(Sum('amount'))['amount__sum']
            all_funds = 0 if all_funds == None else all_funds
            all_loans = 0 if all_loans == None else all_loans
            all_loans = loan.amount
            if (all_funds < all_loans):
                return Response({
                     "message":"this loan cannot be created, funds are not available",
                }, status=status.HTTP_400_BAD_REQUEST)
            else :
                loan.accepted = True;
                loan.save()
                return Response({
                     "message":"Loan accepted",
                }, status=status.HTTP_202_ACCEPTED)
        else:
            loan.accepted = True;
            loan.save()
            return Response({
                    "message":"Loan accepted",
            }, status=status.HTTP_202_ACCEPTED)
    else:
        return Response({
                    "message":"You are not authorised to accept the loan",
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@parser_classes([JSONParser])
def pay_loan(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return Response({
                     "message":"Not Logged in please login first"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        payload = jwt.decode(token, 'secret', algorithm=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({
                     "message":"Not Logged in please login first"}, status=status.HTTP_400_BAD_REQUEST)

    loan = Loan.objects.get(id = request.data.id)
    user = payload['id']
    if (user != loan.user):
         return Response({
                     "message":"Not Authorised to pay loan"}, status=status.HTTP_400_BAD_REQUEST)
    if (loan.accepted == False):
         return Response({
                     "message":"cannot pay this loan"}, status=status.HTTP_400_BAD_REQUEST)
    new_amount = loan.amount - request.data.amount
    if (new_amount < 0):
        loan.delete()
    else :
        loan.amount = new_amount
        loan.save()
