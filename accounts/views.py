from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from django.db import IntegrityError
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import RegistrationSerializer, ChangePasswordSerializer, SetProfileSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from .models import User
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password
from .permissions import IsActive
from shopping.models import Cart
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse

@extend_schema(
    tags=["User"],
    description="This endpoint allows you to register a new user.",
    request=RegistrationSerializer,
    responses= {
        201: OpenApiResponse(),
        400: OpenApiResponse(),
    }
)
class UserRegistrationView(CreateAPIView):
    serializer_class = RegistrationSerializer
    authentication_classes = ()
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            with transaction.atomic():
                user = User.objects.create_user(
                    username=serializer.validated_data['username'],
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password']
                )
                Cart.objects.create(user=user)
                return Response(status=status.HTTP_201_CREATED)

@extend_schema(
    tags=["User"],
    description="This endpoint allows you to log in.",
    responses= {
        201: OpenApiResponse(),
        400: OpenApiResponse(),
    }
)                
class LoginView(ObtainAuthToken):
    authentication_classes = ()


@extend_schema(
    tags=["User"],
    description="This endpoint allows you to log out.",
    responses= {
        200: OpenApiResponse(),
        401: OpenApiResponse(),
    }
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
        
    def get(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)        

@extend_schema(
    tags=["User"],
    description="This endpoint allows you to change your password.",
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(),
        400: OpenApiResponse(),
        401: OpenApiResponse()
    }
)   
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        user = request.user
        if serializer.is_valid(raise_exception=True):
            if not check_password(serializer.validated_data['old_password'], user.password):
                return Response({"message": "The old password is incorrect!"}, status=status.HTTP_400_BAD_REQUEST) 
            if serializer.validated_data['new_password'] == serializer.validated_data['old_password']:
                return Response({"message": "The new password cannot be the same as the old password."}, status=status.HTTP_400_BAD_REQUEST) 
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_200_OK)

@extend_schema(
    tags=["User"],
    description="This endpoint allows you to modify your profile information.",
    request=SetProfileSerializer,
    responses={
        200: OpenApiResponse(response=UserSerializer),
        400: OpenApiResponse(),
        401: OpenApiResponse(),
    }
)              
class SetProfileView(UpdateAPIView):
    http_method_names = ["patch"]
    permission_classes = [IsAuthenticated, IsActive]
    serializer_class = SetProfileSerializer
    response_serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
 
    def update(self, request, *args, **kwargs):
        res = super().update(request, *args, **kwargs)
        return Response(data=self.response_serializer_class(instance=self.get_object(), context={'request': request}).data, status=res.status_code)
    
@extend_schema(
    tags=["User"],
    description="This endpoint allows you to get your profile information.",
    responses={
        200: OpenApiResponse(response=UserSerializer),
        400: OpenApiResponse(),
        401: OpenApiResponse(),
    }
)   
class GetProfileView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    def get_object(self):
        return self.request.user
       