from django.contrib import admin
from .models import CompromisoAgenda, AjusteDesempenio

@admin.register(CompromisoAgenda)
class CompromisoAgendaAdmin(admin.ModelAdmin):
    list_display = ('solicitante', 'responsable', 'fecha_comprometida', 'estado', 'territorio')
    search_fields = ('solicitante', 'responsable__user__username', 'territorio')
    list_filter = ('estado', 'fecha_comprometida')
    date_hierarchy = 'fecha_comprometida'
    list_select_related = ('responsable__user', 'actividad_origen')

@admin.register(AjusteDesempenio)
class AjusteDesempenioAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'periodo', 'concepto', 'valor_porcentaje', 'autorizador')
    list_filter = ('periodo', 'concepto')
    list_select_related = ('funcionario__user', 'periodo', 'autorizador__user')