from django.contrib import admin
from .models import Actividad, Evidencia, ValidacionEvidencia, AtencionSocialGestion

@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ('codigo_evidencia_unico', 'fecha_actividad', 'funcionario', 'item', 'periodo')
    search_fields = (
        'codigo_evidencia_unico',
        'funcionario__user__username',
        'funcionario__user__first_name',
        'funcionario__user__last_name',
        'funcionario__identificador_institucional',
        'descripcion_solicitud'
    )
    list_filter = ('periodo', 'item__cargo', 'funcionario__delegacion', 'fecha_actividad')
    date_hierarchy = 'fecha_actividad'
    list_select_related = ('funcionario__user', 'funcionario__delegacion', 'item', 'periodo')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ('actividad', 'ruta_archivo_url', 'created_at')
    search_fields = ('actividad__codigo_evidencia_unico', 'ruta_archivo_url')
    list_select_related = ('actividad',)

@admin.register(ValidacionEvidencia)
class ValidacionEvidenciaAdmin(admin.ModelAdmin):
    list_display = ('actividad', 'verificador', 'resultado', 'created_at')
    search_fields = (
        'actividad__codigo_evidencia_unico',
        'verificador__user__username',
        'verificador__user__first_name',
        'verificador__user__last_name'
    )
    list_filter = ('resultado',)
    list_select_related = ('actividad', 'verificador__user')

@admin.register(AtencionSocialGestion)
class AtencionSocialGestionAdmin(admin.ModelAdmin):
    list_display = ('actividad', 'numero_gestion', 'tipo_gestion', 'fecha_gestion')
    search_fields = ('actividad__codigo_evidencia_unico', 'tipo_gestion', 'resultado_gestion')
    list_filter = ('tipo_gestion',)
    list_select_related = ('actividad',)