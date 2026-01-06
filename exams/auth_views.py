from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.authtoken.views import ObtainAuthToken  #for login
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication

from .serializers import RegisterSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample, extend_schema_view, OpenApiResponse


@extend_schema_view(
    post=extend_schema(
        description="Register students for the exam. Generates an auth token on successful registration.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["username", "password"]
            }
        },
        responses={
            201: OpenApiResponse(
                description="Registration successful, returns auth token",
                examples=[
                    OpenApiExample(
                        name="RegistrationSuccess",
                        value={
                            "message": "Registration successful",
                            "token": "d412810348669d52d24a3....."
                        },
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Registration failed",
                examples=[
                    OpenApiExample(
                        name="RegistrationFailed",
                        value={"error": "Username already exists"},
                        response_only=True
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name="RegisterRequest",
                summary="Example registration request",
                value={
                    "username": "John Deo",
                    "password": "John2026@"
                },
                request_only=True
            )
        ]
    )
)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            if User.objects.filter(username=username).exists():
                return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(username=username, password=password)
            token = user.auth_token  #signals.py

            return Response({
                "message": "Registration successful",
                "token": token.key
            }, status=201)

        return Response(serializer.errors, status=400)



@extend_schema_view(
    post=extend_schema(
        description="Students login for the exam. Returns a token if credentials are valid.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["username", "password"]
            }
        },
        responses={
            201: OpenApiResponse(
                description="Login successful, returns token",
                examples=[
                    OpenApiExample(
                        name="LoginSuccess",
                        value={"token": "d412810348669d52d24a3....."},
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Invalid credentials",
                examples=[
                    OpenApiExample(
                        name="LoginFailed",
                        value={"error": "Invalid username or password"},
                        response_only=True
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name="LoginRequest",
                summary="Example login request body",
                value={
                    "username": "John Deo",
                    "password": "John2026@"
                },
                request_only=True
            )
        ]
    )
)

class LoginView(ObtainAuthToken):
    authentication_classes = [TokenAuthentication]
    # pass  #behave exactly like the default login view no custom is add.

    def post(self, request, *args, **kwargs):
        # Call the parent class to validate username/password
        response = super().post(request, *args, **kwargs)
        
        # DRF returns only the token by default, but it can be customized
        token = Token.objects.get(key=response.data['token'])
        return Response({
            "token": token.key,
            "user_id": token.user_id,
            "username": token.user.username
        })
