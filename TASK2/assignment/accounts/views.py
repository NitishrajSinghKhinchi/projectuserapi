from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import Userserializer,DetailSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from assignment import settings
from .tokens import account_activation_token
from django.core.mail import send_mail,EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes,force_text
from rest_framework import viewsets
import jwt,datetime
from rest_framework.exceptions import AuthenticationFailed
from accounts import tokens
import razorpay

# Create your views here.
@api_view(['POST'])
def create_user(request):
        if request.method == "POST":
            serializer = Userserializer(data=request.data)
            # print(serializer.data)
            # print(serializer.errors)
            if serializer.is_valid():
                user=serializer.save()
                # print(user)
                # print(user.email,user.pk,user.name)
                current_site = get_current_site(request)
                mail_subject="Activate your account."
                message=render_to_string('accounts/sendemail.html',{
                    'user':user,
                    'domain':current_site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':account_activation_token.make_token(user),
                })
                # print(message)
                recipient_list =user.email
                # print(recipient_list)
                from_email=settings.EMAIL_HOST_USER
                # print(from_email)
                try:
                    send_mail(
                        subject=mail_subject,
                        message=message,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[recipient_list,],
                        fail_silently=False,
                    )
                except:
                    print("Not send")
                return Response({'msg':'Account created Please verify email'},status=status.HTTP_201_CREATED)
            # print(serializer.errors)
        return Response(serializer.errors)

def activate(request,uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user=CustomUser.objects.get(pk=uid)
    except:
        return HttpResponse("Invalid link")
        # user=None
    if user is not None and account_activation_token.check_token(user,token):
        user.is_active = True
        user.save()
        return HttpResponse("Your account activate")
    else:
        return HttpResponse("Link is Invalid")


class LoginViews(APIView):
    def post(self,request):
        email = request.data['email']
        password = request.data['password']
        # print(email)
        # print(password)

        user =CustomUser.objects.filter(email=email).first()
        print(user.id)
        if user is None:
            raise AuthenticationFailed("User not found")
        
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password")

        payload ={
            'id':user.id,
            'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=60),
            'iat':datetime.datetime.utcnow()
        }
        token =jwt.encode(payload,'secret',algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt',value=token,httponly=True)
        response.data ={'jwt':token}
        return response

class UserViews(APIView):
    def get(self,request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("UnAuthenticated")
        try:
            payload=jwt.decode(token,'secret',algorithms='HS256')
        except jwt.ExpiredSignatureError as e:
            raise AuthenticationFailed(e)
        # print(payload['id'])
        user = CustomUser.objects.get(pk=payload['id'])
        # print(user)
        serializer=DetailSerializer(user)
        return Response(serializer.data)

class LogoutViews(APIView):
    def post(self,request):
        response = Response()
        response.delete_cookie('jwt')
        response.data ={'msg':'Successfully Logout'}
        return response



class Payment(APIView):
        def get(self,request):
            token = request.COOKIES.get('jwt')
            if not token:
                raise AuthenticationFailed("UnAuthenticated please login")
            try:
                payload=jwt.decode(token,'secret',algorithms='HS256')
            except jwt.ExpiredSignatureError as e:
                raise AuthenticationFailed(e)
            # print(payload['id'])
            user = CustomUser.objects.get(pk=payload['id'])
            print(user.pk)
            print(user.email)
            # current_site = get_current_site(request)
            client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY,settings.RAZORPAY_API_SECRET_KEY))
            order_amount = 50000
            order_currency = 'INR'
            payment_order=client.order.create(dict(amount=order_amount, currency=order_currency,payment_capture=1))
            payment_order_id=payment_order['id']
            mail_subject="Payment Now"
            messages=render_to_string('accounts/payment.html',{
                    'user':user.name,
                    'amount':500,
                    'api_key':settings.RAZORPAY_API_KEY,
                    'order_id':payment_order_id
            })
            recipient_list = user.email
            # print(recipient_list)
            from_email=settings.EMAIL_HOST_USER
            # print(from_email)
            try:
                msg = EmailMultiAlternatives(mail_subject, messages, from_email, [recipient_list, ])
                msg.attach_alternative(messages, "text/html")
                msg.send()
            except:
                    print("Not send")

            return Response({'msg':'Please check email to payment'},status=status.HTTP_201_CREATED)
            
          
        


    
   
    



    
