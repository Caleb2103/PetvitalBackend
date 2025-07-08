from django.db import models
from django.utils import timezone
import pytz

def get_lima_now():
    return timezone.now().astimezone(pytz.timezone('America/Lima'))

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    contraseña = models.CharField(max_length=20)
    fecha_registro = models.DateTimeField(default=timezone.now)
    userImage = models.CharField(max_length=200, blank=True, null=True)

    @property
    def fecha_registro_lima(self):
        """Retorna la fecha de registro en hora de Lima"""
        lima_tz = pytz.timezone('America/Lima')
        return self.fecha_registro.astimezone(lima_tz)

    def __str__(self):
        return self.nombres

class Mascota(models.Model):
    mascota_id = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    raza = models.CharField(max_length=100)
    genero = models.CharField(max_length=100)
    edad = models.IntegerField()
    unidad_tiempo = models.CharField(max_length=100)
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    esterilizado = models.BooleanField(default=False)
    mascotaImage = models.CharField(max_length=200, blank=True, null=True)
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

class Cita(models.Model):
    tipo_recordatorio = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    fecha = models.DateField()
    hora = models.TimeField()
    nota = models.CharField(max_length=200, blank=True)
    recordatorio = models.CharField(max_length=100, blank=True)
    
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)


class Revision(models.Model):
    titulo = models.CharField(max_length=100)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=200, blank=True)

    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)