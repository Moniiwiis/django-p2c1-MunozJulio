from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel

class Delegacion(BaseModel):
    ESTADO_CHOICES = [('Activa', 'Activa'), ('Inactiva', 'Inactiva')]

    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Activa')
    ambito = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nombre

class Cargo(BaseModel):
    nombre_cargo = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre_cargo

class Funcionario(BaseModel):
    ESTADO_CHOICES = [('Activo', 'Activo'), ('Inactivo', 'Inactivo')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='funcionario')
    identificador_institucional = models.CharField(max_length=20, unique=True)
    delegacion = models.ForeignKey(Delegacion, on_delete=models.RESTRICT, null=True, blank=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.RESTRICT)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Activo')

    def __str__(self):
        return f"{self.user.username} - {self.identificador_institucional}"

class Rol(BaseModel):
    nombre_rol = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_rol

class FuncionarioRol(BaseModel):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('funcionario', 'rol')