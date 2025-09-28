# users/views.py
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


from .serializers import MyTokenObtainPairSerializer
from .serializers import RegisterSerializer


class RegisterView(APIView):
    # // Permitimos el acceso a cualquiera, ya que es un endpoint de registro público.
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)

        # El método is_valid() ejecuta las validaciones del serializer.
        # Si el email ya existe, o falta un campo, lanzará una excepción
        # que DRF convierte en una respuesta 400 Bad Request.
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            # // Una vez el usuario es creado y guardado, generamos sus tokens JWT.
            refresh = RefreshToken.for_user(user)

            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }

            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairView(TokenObtainPairView):
    # // Le indicamos a la vista que use nuestro serializer personalizado.
    serializer_class = MyTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"detail": "Token inválido o expirado."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "No se proporcionó el token de refresco."}, status=status.HTTP_400_BAD_REQUEST)