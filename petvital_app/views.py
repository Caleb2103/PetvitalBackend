from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import render

from .models import *
from .serializers import *
from petvital_app.utils.gemini_api import enviar_mensaje

#Login Usuario
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            contraseña = serializer.validated_data['contraseña']

            try:
                user = User.objects.get(email=email, contraseña=contraseña)

                # Obtener las mascotas del usuario
                mascotas = Mascota.objects.filter(usuario=user)
                mascotas_serializadas = MascotaSerializer(mascotas, many=True).data

                return Response({
                    'message': 'Login exitoso',
                    'user': {
                        'user_id': user.user_id,
                        'nombres': user.nombres,
                        'apellidos': user.apellidos,
                        'email': user.email,
                        'userImage': user.userImage
                    },
                    'pets': mascotas_serializadas
                }, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Register
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(email=serializer.validated_data['email']).exists():
                return Response({'error': 'El email ya está registrado'}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            return Response({
                'message': 'Usuario registrado exitosamente',
                'user_id': user.user_id,
                'nombres': user.nombres,
                'apellidos': user.apellidos,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Obtener datos para HomeScreen
class HomeDataView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({'error': 'user_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verificar que el usuario existe
            user = User.objects.get(user_id=user_id)

            # Obtener mascotas del usuario
            mascotas = Mascota.objects.filter(usuario=user)
            mascotas_data = MascotaSerializer(mascotas, many=True).data

            # Obtener citas del usuario
            citas = Cita.objects.filter(mascota__usuario=user)
            citas_data = CitaSerializer(citas, many=True).data

            return Response({
                'mascotas': mascotas_data,
                'citas': citas_data
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

#Get Usuarios
class GetAllUsersView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserDataSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#Cambiar Contraseña
class ChangePasswordView(APIView):
    def post(self, request, user_id):
        nueva_contraseña = request.data.get('nueva_contraseña')
        if not nueva_contraseña:
            return Response({'error': 'Se requiere una nueva contraseña'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user_id=user_id)
            user.contraseña = nueva_contraseña
            user.save()
            return Response({'message': 'Contraseña actualizada exitosamente'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

#Update Usuario
class UserUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'user_id'

    def update(self, request, *args, **kwargs):
        print(">>> [UPDATE] Datos recibidos:", request.data)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuario actualizado exitosamente"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f">>> [DESTROY] Eliminando usuario ID: {instance.user_id}")
        self.perform_destroy(instance)
        return Response({"message": "Usuario eliminado exitosamente"}, status=status.HTTP_204_NO_CONTENT)

# Crear Mascota
class MascotaCreateView(generics.CreateAPIView):
    serializer_class = MascotaCreateSerializer

    def create(self, request, *args, **kwargs):
        create_serializer = self.get_serializer(data=request.data)
        if create_serializer.is_valid():
            mascota = create_serializer.save()
            response_serializer = MascotaSerializer(mascota)
            return Response({
                "message": "Mascota creada exitosamente",
                "mascota": response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(create_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Listar Mascotas con user_id en query param
class MascotaListView(generics.ListAPIView):
    serializer_class = MascotaSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Mascota.objects.filter(usuario__user_id=user_id)
        else:
            return Mascota.objects.filter(usuario__user_id=1)

# Update y Delete de Mascota
class MascotaUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mascota.objects.all()
    serializer_class = MascotaSerializer
    lookup_field = 'mascota_id'

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({"message": "Mascota actualizada exitosamente"}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Mascota eliminada exitosamente"}, status=status.HTTP_204_NO_CONTENT)

# Crear Cita
class CitaCreateView(generics.CreateAPIView):
    serializer_class = CitaCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print("Datos recibidos:", request.data)
        if serializer.is_valid():
            cita = serializer.save()
            # Usamos el serializer completo para la respuesta
            response_serializer = CitaSerializer(cita)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        print("Errores del serializer:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Listar Citas por query param: user_id, mascota_id
class CitaListView(generics.ListAPIView):
    serializer_class = CitaSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        mascota_id = self.request.query_params.get('mascota_id')

        queryset = Cita.objects.all()

        if mascota_id:
            queryset = queryset.filter(mascota__mascota_id=mascota_id)
        if user_id:
            queryset = queryset.filter(mascota__usuario__user_id=user_id)

        return queryset


class CitaDetailView(generics.RetrieveAPIView):
    serializer_class = CitaSerializer

    def get_queryset(self):
        return Cita.objects.all()

    def get_object(self):
        cita_id = self.kwargs.get('id')
        queryset = self.get_queryset()
        return queryset.get(id=cita_id)

# Update y Delete de Cita
class CitaUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cita.objects.all()
    serializer_class = CitaSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({"message": "Cita actualizada exitosamente"}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Cita eliminada exitosamente"}, status=status.HTTP_204_NO_CONTENT)

# Crear Revision
class RevisionCreateView(generics.CreateAPIView):
    serializer_class = RevisionCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print("Datos recibidos:", request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Revision creada exitosamente"}, status=status.HTTP_201_CREATED)
        print("Errores del serializer:", serializer.errors)  # <-- imprime los errores
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Listar Revisiones por query param: user_id, mascota_id
class RevisionListView(generics.ListAPIView):
    serializer_class = RevisionSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        mascota_id = self.request.query_params.get('mascota_id')

        queryset = Revision.objects.all()

        if mascota_id:
            queryset = queryset.filter(mascota__mascota_id=mascota_id)
        if user_id:
            queryset = queryset.filter(mascota__usuario__user_id=user_id)

        return queryset

# Update y Delete de Cita
class RevisionUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Revision.objects.all()
    serializer_class = RevisionSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({"message": "Revision actualizada exitosamente"}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Revision eliminada exitosamente"}, status=status.HTTP_204_NO_CONTENT)

#Procesar Mensajes IA con Memoria
class ProcesarMensajeIAView(generics.CreateAPIView):
    serializer_class = MensajeIAInputSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                respuesta = enviar_mensaje(serializer.validated_data)
                return Response({"botMessage": respuesta}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)