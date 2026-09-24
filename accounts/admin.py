from django.contrib import admin
from .models import Delegacion, Cargo, Funcionario, Rol, FuncionarioRol

@admin.register(Delegacion)
class DelegacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado', 'ambito', 'created_at')
    search_fields = ('nombre', 'ambito')
    list_filter = ('estado',)

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nombre_cargo', 'descripcion', 'created_at')
    search_fields = ('nombre_cargo',)

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'identificador_institucional', 'delegacion', 'cargo', 'estado')
    search_fields = ('user__username', 'identificador_institucional', 'user__first_name', 'user__last_name')
    list_filter = ('delegacion', 'cargo', 'estado')
    list_select_related = ('user', 'delegacion', 'cargo')  # Optimiza consultas de FK (Lámina 11)

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre_rol', 'created_at')

@admin.register(FuncionarioRol)
class FuncionarioRolAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'rol')
    list_select_related = ('funcionario', 'rol')