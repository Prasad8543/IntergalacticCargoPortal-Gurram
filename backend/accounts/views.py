from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.jwt import generate_tokens_for_user
from core.pagination import DefaultCursorPagination
from core.token_blacklist import blacklist_token

from .models import User
from .permissions import AdminUserPermission, StandardUserPermission
from .serializers import LoginSerializer, SignupSerializer, UserSerializer


class SignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        access, refresh = generate_tokens_for_user(user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'access': access,
                'refresh': refresh,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Open endpoint — authenticate with email and password."""

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data['email'].strip().lower()
        password = serializer.validated_data['password']

        from django.contrib.auth import authenticate

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access, refresh = generate_tokens_for_user(user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'access': access,
                'refresh': refresh,
            }
        )


class UserListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, AdminUserPermission]
    pagination_class = DefaultCursorPagination
    queryset = User.objects.select_related('role').order_by('id')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SignupSerializer
        return UserSerializer


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, StandardUserPermission]

    def get(self, request, pk):
        try:
            user = User.objects.select_related('role').get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response(
                {'error': 'Authorization header with Bearer token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = auth_header[7:].strip()
        blacklist_token(token)
        return Response({'message': 'Logged out successfully.'})
