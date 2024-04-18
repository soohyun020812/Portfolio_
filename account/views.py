
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from account.serializers import CustomUserSerializer
from rest_framework import viewsets
from account.models import CustomUser

from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.token_blacklist import models

from account.models import CustomUser
from account.serializers import CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class SignUpView(CreateAPIView):
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise PermissionDenied("로그인 실패")
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "로그인 성공",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"message": "로그인 실패"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        # 세션 종료
        logout(request)

        # 리프레시 토큰 무효화
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                user_id = token.payload.get("user_id")
                if user_id:
                    models.OutstandingToken.objects.filter(user_id=user_id).delete()
                return Response({"message": "로그아웃 성공"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"message": "리프레시 토큰 무효화 실패"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "리프레시 토큰이 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        data = request.data
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            if not user._meta.get_field("username").clean(data["username"], user):
                return Response(
                    {"error": "유효하지 않은 형식입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if "age" in data and not user._meta.get_field("age").clean(
                data["age"], user
            ):
                return Response(
                    {"error": "유효하지 않은 나이입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if "profile_picture" in data:
                profile_picture = data["profile_picture"]
                max_size = 10 * 1024 * 1024  # 10MB
                if profile_picture.size > max_size:
                    return Response(
                        {"error": "프로필 사진의 크기가 너무 큽니다."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "탈퇴 성공"}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request):
        raise MethodNotAllowed("PATCH")
