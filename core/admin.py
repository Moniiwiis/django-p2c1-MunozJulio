from django.contrib import admin
from core.access import has_capability, scope_queryset

class SoftDeleteListFilter(admin.SimpleListFilter):
    title = 'Estado de Borrado (Soft Delete)'
    parameter_name = 'soft_deleted'

    def lookups(self, request, model_admin):
        return (
            ('activos', 'Solo Activos (Predeterminado)'),
            ('eliminados', 'Solo Eliminados (Soft Delete)'),
            ('todos', 'Todos (Activos + Eliminados)'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'eliminados':
            return queryset.filter(deleted_at__isnull=False)
        elif val == 'todos':
            return queryset
        # Por defecto (None o 'activos') mostramos solo los registros activos
        return queryset.filter(deleted_at__isnull=True)

class BaseScopedModelAdmin(admin.ModelAdmin):
    """
    Clase base para que todos los usuarios staff (delegados, funcionarios) tengan
    permisos de módulo y vista/edición en Django Admin, aplicando luego la restricción 
    de visibilidad (Scoping por Delegación) mediante get_queryset() y soporte de borrado lógico.
    """
    def get_queryset(self, request):
        if hasattr(self.model, 'all_objects'):
            queryset = self.model.all_objects.all()
        else:
            queryset = super().get_queryset(request)
        section = self.get_access_section()
        return scope_queryset(request.user, section, queryset) if section else queryset

    def get_list_display(self, request):
        fields = list(super().get_list_display(request))
        for timestamp in ('updated_at', 'deleted_at'):
            if timestamp in {field.name for field in self.model._meta.fields} and timestamp not in fields:
                fields.append(timestamp)
        return fields

    def get_access_section(self):
        return {
            'accounts': 'funcionarios',
            'activities': 'actividades',
            'agenda': 'agenda',
            'configuration': 'configuracion',
            'analytics': 'reportes',
        }.get(self.model._meta.app_label)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        target_section = {
            'accounts': 'funcionarios',
            'activities': 'actividades',
            'agenda': 'agenda',
            'configuration': 'configuracion',
        }.get(db_field.remote_field.model._meta.app_label)
        if target_section:
            kwargs['queryset'] = scope_queryset(
                request.user,
                target_section,
                db_field.remote_field.model._default_manager.all(),
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_list_filter(self, request):
        filters = list(super().get_list_filter(request) or [])
        if SoftDeleteListFilter not in filters and hasattr(self.model, 'deleted_at'):
            filters.append(SoftDeleteListFilter)
        return filters

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj) or [])
        for timestamp in ('created_at', 'updated_at', 'deleted_at'):
            if hasattr(self.model, timestamp) and timestamp not in fields:
                fields.append(timestamp)
        return fields

    def has_module_permission(self, request):
        section = self.get_access_section()
        return request.user.is_active and section is not None and any(
            has_capability(request.user, section, action)
            for action in ('view', 'create', 'edit', 'delete', 'validate')
        )


    def has_view_permission(self, request, obj=None):
        return request.user.is_active and has_capability(request.user, self.get_access_section())

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and has_capability(request.user, self.get_access_section(), 'edit')

    def has_add_permission(self, request):
        return request.user.is_active and has_capability(request.user, self.get_access_section(), 'create')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and has_capability(request.user, self.get_access_section(), 'delete')

    def delete_model(self, request, obj):
        """Asegura que la eliminación individual ejecute el borrado lógico (Soft Delete)."""
        obj.delete()

    def delete_queryset(self, request, queryset):
        """Asegura que la eliminación masiva ejecute el borrado lógico (Soft Delete)."""
        queryset.delete()


