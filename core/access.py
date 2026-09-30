from functools import wraps

from django.http import HttpResponseForbidden
from django.db.models import Q

from accounts.models import Cargo, Delegacion, Funcionario, FuncionarioRol, Rol


ADMIN = 'Administrador'
COORDINATOR = 'Coordinador del sistema'
DELEGATE = 'Delegado / Jefatura'
OFFICER = 'Funcionario'
VERIFIER = 'Verificador'
CONSULTANT = 'Usuario de consulta'

ROLE_CAPABILITIES = {
    ADMIN: {
        'inicio': {'view'},
        'funcionarios': {'view', 'create', 'edit', 'delete'},
        'actividades': {'view', 'create', 'edit', 'delete', 'validate'},
        'agenda': {'view', 'create', 'edit', 'delete'},
        'configuracion': {'view', 'create', 'edit', 'delete'},
        'reportes': {'view'},
    },
    COORDINATOR: {
        'inicio': {'view'},
        'funcionarios': {'view'},
        'actividades': {'view'},
        'agenda': {'view'},
        'configuracion': {'view'},
        'reportes': {'view'},
    },
    DELEGATE: {
        'inicio': {'view'},
        'funcionarios': {'view'},
        'actividades': {'view', 'create', 'edit'},
        'agenda': {'view', 'create', 'edit'},
        'reportes': {'view'},
    },
    OFFICER: {
        'inicio': {'view'},
        'actividades': {'view', 'create', 'edit'},
        'agenda': {'view', 'create', 'edit'},
    },
    VERIFIER: {
        'inicio': {'view'},
        'actividades': {'view', 'validate'},
        'reportes': {'view'},
    },
    CONSULTANT: {
        'inicio': {'view'},
        'reportes': {'view'},
    },
}


def get_user_roles(user):
    if not user.is_authenticated:
        return set()
    if user.is_superuser:
        return {ADMIN}

    try:
        return set(
            FuncionarioRol.objects.filter(funcionario=user.funcionario)
            .values_list('rol__nombre_rol', flat=True)
        )
    except (AttributeError, user._meta.model.DoesNotExist):
        return set()


def has_capability(user, section, action='view'):
    roles = get_user_roles(user)
    return any(
        action in ROLE_CAPABILITIES.get(role, {}).get(section, set())
        for role in roles
    )


def access_required(section, action='view'):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not has_capability(request.user, section, action):
                return HttpResponseForbidden('No tienes permisos para realizar esta acción.')
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def scope_queryset(user, section, queryset):
    roles = get_user_roles(user)
    if ADMIN in roles or roles & {COORDINATOR, CONSULTANT}:
        return queryset

    try:
        funcionario = user.funcionario
    except (AttributeError, user._meta.model.DoesNotExist):
        return queryset.none()

    if DELEGATE in roles and funcionario.delegacion_id:
        if section == 'funcionarios':
            if queryset.model is Funcionario:
                return queryset.filter(delegacion=funcionario.delegacion)
            if queryset.model is FuncionarioRol:
                return queryset.filter(funcionario__delegacion=funcionario.delegacion)
            if queryset.model is Delegacion:
                return queryset.filter(pk=funcionario.delegacion_id)
            if queryset.model is Cargo:
                return queryset.filter(pk=funcionario.cargo_id)
            if queryset.model is Rol:
                return queryset.filter(funcionariorol__funcionario__delegacion=funcionario.delegacion).distinct()
            return queryset.none()
        if section == 'actividades':
            if queryset.model is Funcionario:
                return queryset.filter(delegacion=funcionario.delegacion)
            return queryset.filter(funcionario__delegacion=funcionario.delegacion) if hasattr(queryset.model, 'funcionario') else queryset.filter(actividad__funcionario__delegacion=funcionario.delegacion)
        if section == 'agenda':
            if queryset.model is Funcionario:
                return queryset.filter(delegacion=funcionario.delegacion)
            return queryset.filter(responsable__delegacion=funcionario.delegacion) if hasattr(queryset.model, 'responsable') else queryset.filter(funcionario__delegacion=funcionario.delegacion)
        if section == 'configuracion':
            return queryset.filter(
                Q(funcionario__delegacion=funcionario.delegacion)
                | Q(item__cargo=funcionario.cargo)
                | Q(funcionario=funcionario)
            ).distinct()

    if OFFICER in roles:
        if section == 'funcionarios':
            if queryset.model is Funcionario:
                return queryset.filter(pk=funcionario.pk)
            if queryset.model is FuncionarioRol:
                return queryset.filter(funcionario=funcionario)
            if queryset.model is Cargo:
                return queryset.filter(pk=funcionario.cargo_id)
            if queryset.model is Rol:
                return queryset.filter(funcionariorol__funcionario=funcionario).distinct()
            if queryset.model is Delegacion:
                return queryset.filter(pk=funcionario.delegacion_id) if funcionario.delegacion_id else queryset.none()
            return queryset.none()
        if section == 'actividades':
            if queryset.model is Funcionario:
                return queryset.filter(pk=funcionario.pk)
            return queryset.filter(funcionario=funcionario) if hasattr(queryset.model, 'funcionario') else queryset.filter(actividad__funcionario=funcionario)
        if section == 'agenda':
            if queryset.model is Funcionario:
                return queryset.filter(pk=funcionario.pk)
            return queryset.filter(responsable=funcionario) if hasattr(queryset.model, 'responsable') else queryset.filter(funcionario=funcionario)
        if section == 'configuracion':
            return queryset.filter(Q(funcionario=funcionario) | Q(item__cargo=funcionario.cargo))

    if VERIFIER in roles and section == 'actividades':
        return queryset

    return queryset.none()


def get_actor_context(user):
    roles = get_user_roles(user)
    primary_role = next(iter(sorted(roles)), 'Sin rol asignado')
    return {
        'actor_role': primary_role,
        'actor_roles': roles,
        'can_view_staff': has_capability(user, 'funcionarios'),
        'can_manage_staff': has_capability(user, 'funcionarios', 'create'),
        'can_view_activities': has_capability(user, 'actividades'),
        'can_create_activities': has_capability(user, 'actividades', 'create'),
        'can_edit_activities': has_capability(user, 'actividades', 'edit'),
        'can_delete_activities': has_capability(user, 'actividades', 'delete'),
        'can_validate_activities': has_capability(user, 'actividades', 'validate'),
        'can_view_agenda': has_capability(user, 'agenda'),
        'can_create_agenda': has_capability(user, 'agenda', 'create'),
        'can_edit_agenda': has_capability(user, 'agenda', 'edit'),
        'can_delete_agenda': has_capability(user, 'agenda', 'delete'),
        'can_manage_configuration': has_capability(user, 'configuracion', 'create'),
        'can_view_configuration': has_capability(user, 'configuracion'),
        'can_view_reports': has_capability(user, 'reportes'),
    }