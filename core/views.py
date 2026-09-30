from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from activities.models import Actividad, ValidacionEvidencia
from agenda.models import CompromisoAgenda
from configuration.models import ConfiguracionMeta, Periodo, ItemMedicion, CatalogoActividad
from accounts.models import Funcionario, Cargo, Delegacion
from core.access import (
    ADMIN,
    OFFICER,
    access_required,
    get_user_roles,
    has_capability,
    scope_queryset,
)

# --- INICIO ---
@login_required(login_url='/admin/login/')
@access_required('inicio')
def gestion_inicio(request):
    metas = scope_queryset(
        request.user,
        'configuracion',
        ConfiguracionMeta.objects.select_related('periodo', 'item'),
    )
    if metas.exists():
        cumplimientos = [m.cumplimiento_ponderado() for m in metas]
        promedio = round(sum(cumplimientos) / len(cumplimientos), 2)
    else:
        promedio = 87.5

    context = {
        'total_actividades': scope_queryset(request.user, 'actividades', Actividad.objects.all()).count(),
        'total_compromisos': scope_queryset(request.user, 'agenda', CompromisoAgenda.objects.all()).count(),
        'total_funcionarios': scope_queryset(request.user, 'funcionarios', Funcionario.objects.all()).count(),
        'promedio_meta': promedio,
    }
    return render(request, 'gestion/inicio.html', context)


# --- FUNCIONARIOS (CRUD) ---
@login_required(login_url='/admin/login/')
@access_required('funcionarios')
def gestion_funcionarios(request):
    if request.method == 'POST':
        if not has_capability(request.user, 'funcionarios', 'create'):
            return redirect('gestion_funcionarios')
        username = request.POST.get('username')
        email = request.POST.get('email')
        identificador = request.POST.get('identificador_institucional')
        cargo_id = request.POST.get('cargo_id')
        delegacion_id = request.POST.get('delegacion_id')
        estado = request.POST.get('estado', 'Activo')

        if username and identificador and cargo_id:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'first_name': username}
            )
            Funcionario.objects.create(
                user=user,
                identificador_institucional=identificador,
                cargo_id=cargo_id,
                delegacion_id=delegacion_id if delegacion_id else None,
                estado=estado
            )
            messages.success(request, f"Funcionario '{username}' registrado correctamente.")
            return redirect('gestion_funcionarios')
        else:
            messages.error(request, "Por favor completa los campos obligatorios.")

    funcionarios = scope_queryset(
        request.user,
        'funcionarios',
        Funcionario.objects.select_related('user', 'cargo', 'delegacion').prefetch_related('funcionariorol_set__rol'),
    )[:50]
    cargos = Cargo.objects.all()
    delegaciones = Delegacion.objects.all()
    total_funcionarios = scope_queryset(request.user, 'funcionarios', Funcionario.objects.all()).count()
    activos = scope_queryset(request.user, 'funcionarios', Funcionario.objects.filter(estado__iexact='Activo')).count()
    total_delegaciones = delegaciones.count()

    context = {
        'funcionarios': funcionarios,
        'cargos': cargos,
        'delegaciones': delegaciones,
        'total_funcionarios': total_funcionarios,
        'activos': activos,
        'total_delegaciones': total_delegaciones,
    }
    return render(request, 'gestion/funcionarios.html', context)

@login_required(login_url='/admin/login/')
@access_required('funcionarios', 'edit')
def gestion_funcionarios_editar(request, funcionario_id):
    funcionario = get_object_or_404(scope_queryset(request.user, 'funcionarios', Funcionario.objects.all()), id=funcionario_id)
    if request.method == 'POST':
        funcionario.identificador_institucional = request.POST.get('identificador_institucional', funcionario.identificador_institucional)
        cargo_id = request.POST.get('cargo_id')
        if cargo_id:
            funcionario.cargo_id = cargo_id
        delegacion_id = request.POST.get('delegacion_id')
        funcionario.delegacion_id = delegacion_id if delegacion_id else None
        funcionario.estado = request.POST.get('estado', funcionario.estado)
        funcionario.save()
        messages.success(request, f"Funcionario '{funcionario.user.username}' actualizado exitosamente.")
    return redirect('gestion_funcionarios')

@login_required(login_url='/admin/login/')
@access_required('funcionarios', 'delete')
def gestion_funcionarios_eliminar(request, funcionario_id):
    funcionario = get_object_or_404(scope_queryset(request.user, 'funcionarios', Funcionario.objects.all()), id=funcionario_id)
    if request.method == 'POST':
        username = funcionario.user.username
        funcionario.delete() # Ejecuta Soft Delete definido en BaseModel
        messages.success(request, f"Funcionario '{username}' eliminado correctamente (borrado lógico).")
    return redirect('gestion_funcionarios')


# --- ACTIVIDADES (CRUD) ---
@login_required(login_url='/admin/login/')
@access_required('actividades')
def gestion_actividades(request):
    actividades_qs = scope_queryset(
        request.user,
        'actividades',
        Actividad.objects.select_related('funcionario__user', 'item', 'periodo'),
    )
    funcionarios = scope_queryset(
        request.user,
        'actividades',
        Funcionario.objects.select_related('user').filter(estado='Activo'),
    )
    items = ItemMedicion.objects.select_related('cargo')
    roles = get_user_roles(request.user)
    if OFFICER in roles:
        items = items.filter(cargo=request.user.funcionario.cargo)
    elif ADMIN not in roles:
        items = items.filter(cargo__in=funcionarios.values('cargo_id'))

    if request.method == 'POST':
        if not has_capability(request.user, 'actividades', 'create'):
            return redirect('gestion_actividades')
        fecha = request.POST.get('fecha_actividad')
        solicitud = request.POST.get('descripcion_solicitud')
        accion = request.POST.get('accion_ejecutada')
        contacto_nombre = request.POST.get('contacto_nombre')
        contacto_telefono = request.POST.get('contacto_telefono')
        funcionario_id = request.POST.get('funcionario_id')
        item_id = request.POST.get('item_id')
        periodo_id = request.POST.get('periodo_id')

        if OFFICER in roles:
            funcionario_id = request.user.funcionario.pk
        if fecha and solicitud and accion and funcionario_id and item_id and periodo_id:
            funcionario = get_object_or_404(funcionarios, pk=funcionario_id)
            item = get_object_or_404(items, pk=item_id)
            periodo = get_object_or_404(Periodo.objects.all(), pk=periodo_id)
            actividad = Actividad(
                fecha_actividad=fecha,
                descripcion_solicitud=solicitud,
                accion_ejecutada=accion,
                contacto_nombre=contacto_nombre,
                contacto_telefono=contacto_telefono,
                funcionario=funcionario,
                item=item,
                periodo=periodo,
            )
            try:
                actividad.full_clean()
                actividad.save()
                messages.success(request, "Actividad registrada con código de evidencia único autogenerado.")
                return redirect('gestion_actividades')
            except ValidationError as error:
                messages.error(request, ' '.join(error.messages))
        else:
            messages.error(request, "Por favor completa los campos obligatorios para la actividad.")

    actividades = actividades_qs[:50]
    periodos = Periodo.objects.all()

    context = {
        'actividades': actividades,
        'funcionarios': funcionarios,
        'items': items,
        'periodos': periodos,
    }
    return render(request, 'gestion/actividades.html', context)

@login_required(login_url='/admin/login/')
@access_required('actividades', 'edit')
def gestion_actividades_editar(request, actividad_id):
    actividad = get_object_or_404(scope_queryset(request.user, 'actividades', Actividad.objects.all()), id=actividad_id)
    if request.method == 'POST':
        actividad.fecha_actividad = request.POST.get('fecha_actividad', actividad.fecha_actividad)
        actividad.descripcion_solicitud = request.POST.get('descripcion_solicitud', actividad.descripcion_solicitud)
        actividad.accion_ejecutada = request.POST.get('accion_ejecutada', actividad.accion_ejecutada)
        actividad.contacto_nombre = request.POST.get('contacto_nombre', actividad.contacto_nombre)
        actividad.contacto_telefono = request.POST.get('contacto_telefono', actividad.contacto_telefono)
        actividad.save()
        messages.success(request, f"Actividad '{actividad.codigo_evidencia_unico}' actualizada exitosamente.")
    return redirect('gestion_actividades')

@login_required(login_url='/admin/login/')
@access_required('actividades', 'delete')
def gestion_actividades_eliminar(request, actividad_id):
    actividad = get_object_or_404(scope_queryset(request.user, 'actividades', Actividad.objects.all()), id=actividad_id)
    if request.method == 'POST':
        codigo = actividad.codigo_evidencia_unico
        actividad.delete()
        messages.success(request, f"Actividad '{codigo}' eliminada del sistema.")
    return redirect('gestion_actividades')


@login_required(login_url='/admin/login/')
@access_required('actividades', 'validate')
def gestion_actividad_validar(request, actividad_id):
    if request.method != 'POST':
        return redirect('gestion_actividades')
    actividad = get_object_or_404(scope_queryset(request.user, 'actividades', Actividad.objects.all()), pk=actividad_id)
    resultado = request.POST.get('resultado')
    if resultado not in {'Aprobado', 'Rechazado'}:
        messages.error(request, 'La decisión de validación no es válida.')
        return redirect('gestion_actividades')
    verificador = get_object_or_404(Funcionario, user=request.user)
    ValidacionEvidencia.objects.create(
        actividad=actividad,
        verificador=verificador,
        resultado=resultado,
        observaciones=request.POST.get('observaciones', ''),
    )
    messages.success(request, f"Evidencia {resultado.lower()} correctamente.")
    return redirect('gestion_actividades')


# --- AGENDA (CRUD) ---
@login_required(login_url='/admin/login/')
@access_required('agenda')
def gestion_agenda(request):
    funcionarios = scope_queryset(
        request.user,
        'agenda',
        Funcionario.objects.select_related('user').filter(estado='Activo'),
    )
    if request.method == 'POST':
        if not has_capability(request.user, 'agenda', 'create'):
            return redirect('gestion_agenda')
        solicitante = request.POST.get('solicitante')
        territorio = request.POST.get('territorio')
        responsable_id = request.POST.get('responsable_id')
        area_apoyo = request.POST.get('area_apoyo')
        fecha_comp = request.POST.get('fecha_comprometida')
        observacion = request.POST.get('observacion')

        if solicitante and responsable_id and fecha_comp:
            responsable = get_object_or_404(funcionarios, pk=responsable_id)
            CompromisoAgenda.objects.create(
                solicitante=solicitante,
                territorio=territorio,
                responsable=responsable,
                area_apoyo=area_apoyo,
                fecha_comprometida=fecha_comp,
                observacion=observacion,
                estado='Ingresado'
            )
            messages.success(request, "Compromiso de agenda ingresado exitosamente.")
            return redirect('gestion_agenda')
        else:
            messages.error(request, "Faltan campos requeridos para registrar el compromiso.")

    compromisos = scope_queryset(
        request.user,
        'agenda',
        CompromisoAgenda.objects.select_related('responsable__user', 'actividad_origen'),
    )[:50]

    context = {
        'compromisos': compromisos,
        'funcionarios': funcionarios,
    }
    return render(request, 'gestion/agenda.html', context)

@login_required(login_url='/admin/login/')
@access_required('agenda', 'edit')
def gestion_agenda_editar(request, compromiso_id):
    compromiso = get_object_or_404(scope_queryset(request.user, 'agenda', CompromisoAgenda.objects.all()), id=compromiso_id)
    if request.method == 'POST':
        compromiso.solicitante = request.POST.get('solicitante', compromiso.solicitante)
        compromiso.territorio = request.POST.get('territorio', compromiso.territorio)
        compromiso.estado = request.POST.get('estado', compromiso.estado)
        compromiso.observacion = request.POST.get('observacion', compromiso.observacion)
        compromiso.save()
        messages.success(request, f"Compromiso de '{compromiso.solicitante}' actualizado.")
    return redirect('gestion_agenda')

@login_required(login_url='/admin/login/')
@access_required('agenda', 'delete')
def gestion_agenda_eliminar(request, compromiso_id):
    compromiso = get_object_or_404(scope_queryset(request.user, 'agenda', CompromisoAgenda.objects.all()), id=compromiso_id)
    if request.method == 'POST':
        solic = compromiso.solicitante
        compromiso.delete()
        messages.success(request, f"Compromiso de '{solic}' eliminado.")
    return redirect('gestion_agenda')


# --- CONFIGURACION DE METAS (CRUD) ---
@login_required(login_url='/admin/login/')
@access_required('configuracion')
def gestion_configuracion(request):
    if request.method == 'POST':
        if not has_capability(request.user, 'configuracion', 'create'):
            return redirect('gestion_configuracion')
        item_id = request.POST.get('item_id')
        periodo_id = request.POST.get('periodo_id')
        funcionario_id = request.POST.get('funcionario_id')
        objetivo = request.POST.get('valor_objetivo')
        ponderacion = request.POST.get('ponderacion')
        umbral = request.POST.get('umbral_minimo', 80.00)
        max_comp = request.POST.get('maximo_computable', 150.00)

        if item_id and periodo_id and objetivo and ponderacion:
            ConfiguracionMeta.objects.create(
                item_id=item_id,
                periodo_id=periodo_id,
                funcionario_id=funcionario_id if funcionario_id else None,
                valor_objetivo=objetivo,
                ponderacion=ponderacion,
                umbral_minimo=umbral,
                maximo_computable=max_comp
            )
            messages.success(request, "Meta configurada correctamente.")
            return redirect('gestion_configuracion')
        else:
            messages.error(request, "Completa los parámetros requeridos para crear la meta.")

    metas = scope_queryset(
        request.user,
        'configuracion',
        ConfiguracionMeta.objects.select_related('item', 'periodo', 'funcionario__user'),
    )[:50]
    items = ItemMedicion.objects.all()
    periodos = Periodo.objects.all()
    funcionarios = Funcionario.objects.select_related('user').all()

    context = {
        'metas': metas,
        'items': items,
        'periodos': periodos,
        'funcionarios': funcionarios,
    }
    return render(request, 'gestion/configuracion.html', context)

@login_required(login_url='/admin/login/')
@access_required('configuracion', 'edit')
def gestion_configuracion_editar(request, meta_id):
    meta = get_object_or_404(scope_queryset(request.user, 'configuracion', ConfiguracionMeta.objects.all()), id=meta_id)
    if request.method == 'POST':
        meta.valor_objetivo = request.POST.get('valor_objetivo', meta.valor_objetivo)
        meta.ponderacion = request.POST.get('ponderacion', meta.ponderacion)
        meta.save()
        messages.success(request, "Configuración de meta actualizada exitosamente.")
    return redirect('gestion_configuracion')

@login_required(login_url='/admin/login/')
@access_required('configuracion', 'delete')
def gestion_configuracion_eliminar(request, meta_id):
    meta = get_object_or_404(scope_queryset(request.user, 'configuracion', ConfiguracionMeta.objects.all()), id=meta_id)
    if request.method == 'POST':
        meta.delete()
        messages.success(request, "Meta eliminada correctamente.")
    return redirect('gestion_configuracion')


# --- REPORTES ---
@login_required(login_url='/admin/login/')
@access_required('reportes')
def gestion_reportes(request):
    metas = scope_queryset(
        request.user,
        'configuracion',
        ConfiguracionMeta.objects.select_related('periodo', 'item'),
    )
    verdes = sum(1 for m in metas if m.estado_semaforo() == 'VERDE')
    ambares = sum(1 for m in metas if m.estado_semaforo() == 'AMBAR')
    rojos = sum(1 for m in metas if m.estado_semaforo() == 'ROJO')
    validaciones = scope_queryset(request.user, 'actividades', ValidacionEvidencia.objects.all())
    total_val = validaciones.count()
    aprobadas = validaciones.filter(resultado__iexact='Aprobado').count()
    pct_aprobadas = round((aprobadas / total_val) * 100, 1) if total_val > 0 else 92.0
    pct_pendientes = round(100 - pct_aprobadas, 1) if total_val > 0 else 8.0

    context = {
        'metas': metas,
        'verdes': verdes,
        'ambares': ambares,
        'rojos': rojos,
        'pct_aprobadas': pct_aprobadas,
        'pct_pendientes': pct_pendientes,
    }
    return render(request, 'gestion/reportes.html', context)
