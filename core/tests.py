from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from accounts.models import Cargo, Delegacion, Funcionario, FuncionarioRol, Rol
from activities.models import Actividad, ValidacionEvidencia
from agenda.admin import CompromisoAgendaAdmin
from agenda.models import CompromisoAgenda
from activities.admin import ActividadAdmin
from configuration.models import CatalogoActividad, ItemMedicion, Periodo
from core.access import (
	ADMIN,
	CONSULTANT,
	COORDINATOR,
	DELEGATE,
	OFFICER,
	VERIFIER,
	has_capability,
)


class ActorCapabilityTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='actor', password='test-pass')
		cargo = Cargo.objects.create(nombre_cargo='Cargo de prueba')
		self.funcionario = Funcionario.objects.create(
			user=self.user,
			identificador_institucional='ACT-001',
			cargo=cargo,
		)

	def assign_role(self, role_name):
		role, _ = Rol.objects.get_or_create(nombre_rol=role_name)
		FuncionarioRol.objects.create(funcionario=self.funcionario, rol=role)

	def test_administrator_can_manage_every_module(self):
		self.user.is_superuser = True
		self.assertTrue(has_capability(self.user, 'configuracion', 'delete'))
		self.assertTrue(has_capability(self.user, 'actividades', 'validate'))

	def test_coordinator_and_consultant_are_read_only(self):
		for role_name in (COORDINATOR, CONSULTANT):
			with self.subTest(role=role_name):
				FuncionarioRol.objects.all().delete()
				self.assign_role(role_name)
				self.assertTrue(has_capability(self.user, 'reportes', 'view'))
				self.assertFalse(has_capability(self.user, 'agenda', 'edit'))

	def test_delegate_and_officer_can_register_but_not_delete(self):
		for role_name in (DELEGATE, OFFICER):
			with self.subTest(role=role_name):
				FuncionarioRol.objects.all().delete()
				self.assign_role(role_name)
				self.assertTrue(has_capability(self.user, 'actividades', 'create'))
				self.assertFalse(has_capability(self.user, 'actividades', 'delete'))

	def test_verifier_can_validate_without_editing_records(self):
		self.assign_role(VERIFIER)
		self.assertTrue(has_capability(self.user, 'actividades', 'validate'))
		self.assertFalse(has_capability(self.user, 'actividades', 'edit'))

	def test_user_without_role_has_no_business_access(self):
		self.assertFalse(has_capability(self.user, 'actividades', 'view'))


class ActorViewAccessTests(TestCase):
	def setUp(self):
		self.cargo = Cargo.objects.create(nombre_cargo='Gestor de prueba')
		self.centro = Delegacion.objects.create(nombre='Delegación Centro')
		self.companias = Delegacion.objects.create(nombre='Delegación Compañías')
		self.periodo = Periodo.objects.create(
			fecha_inicio='2026-01-01',
			fecha_termino='2026-12-31',
			dias_computables=365,
		)
		catalogo = CatalogoActividad.objects.create(
			tipo_actividad='Atención',
			servicio='Servicio de prueba',
		)
		self.item = ItemMedicion.objects.create(
			cargo=self.cargo,
			catalogo=catalogo,
			nombre_item='Atenciones',
		)
		self.delegate, self.delegate_profile = self.create_actor(
			'delegada', DELEGATE, self.centro
		)
		self.other_user, self.other_profile = self.create_actor(
			'otro', OFFICER, self.companias
		)
		self.officer, self.officer_profile = self.create_actor(
			'funcionario', OFFICER, self.centro
		)
		self.verifier, self.verifier_profile = self.create_actor(
			'verificador', VERIFIER, self.centro
		)
		self.coordinator, _ = self.create_actor('coordinador', COORDINATOR)
		self.consultant, _ = self.create_actor('consulta', CONSULTANT)

		self.local_activity = self.create_activity(self.officer_profile, 'Actividad local')
		self.foreign_activity = self.create_activity(self.other_profile, 'Actividad ajena')

	def create_actor(self, username, role_name, delegation=None):
		user = User.objects.create_user(username=username, password='test-pass', is_staff=True)
		profile = Funcionario.objects.create(
			user=user,
			identificador_institucional=f'{username}-ID',
			cargo=self.cargo,
			delegacion=delegation,
		)
		role, _ = Rol.objects.get_or_create(nombre_rol=role_name)
		FuncionarioRol.objects.create(funcionario=profile, rol=role)
		return user, profile

	def create_activity(self, funcionario, description):
		return Actividad.objects.create(
			fecha_actividad='2026-06-01',
			descripcion_solicitud=description,
			accion_ejecutada='Acción de prueba',
			funcionario=funcionario,
			item=self.item,
			periodo=self.periodo,
		)

	def test_anonymous_users_are_redirected_to_login(self):
		response = self.client.get(reverse('gestion_actividades'))
		self.assertEqual(response.status_code, 302)
		self.assertIn('/admin/login/', response.url)

	def test_consultant_can_read_reports_but_not_operational_modules(self):
		self.client.force_login(self.consultant)
		self.assertEqual(self.client.get(reverse('gestion_reportes')).status_code, 200)
		self.assertEqual(self.client.get(reverse('gestion_actividades')).status_code, 403)

	def test_coordinator_sees_configuration_without_write_controls(self):
		self.client.force_login(self.coordinator)
		response = self.client.get(reverse('gestion_configuracion'))
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, 'Nueva Meta SGR')

	def test_delegate_only_sees_and_edits_records_in_own_delegation(self):
		self.client.force_login(self.delegate)
		response = self.client.get(reverse('gestion_actividades'))
		self.assertContains(response, 'Actividad local')
		self.assertNotContains(response, 'Actividad ajena')

		response = self.client.post(
			reverse('gestion_actividades_editar', args=[self.foreign_activity.pk]),
			{'descripcion_solicitud': 'Cambio no autorizado'},
		)
		self.assertEqual(response.status_code, 404)
		self.foreign_activity.refresh_from_db()
		self.assertEqual(self.foreign_activity.descripcion_solicitud, 'Actividad ajena')

	def test_officer_cannot_create_activity_for_another_user(self):
		self.client.force_login(self.officer)
		response = self.client.post(reverse('gestion_actividades'), {
			'fecha_actividad': '2026-06-02',
			'descripcion_solicitud': 'Registro propio',
			'accion_ejecutada': 'Acción realizada',
			'funcionario_id': self.other_profile.pk,
			'item_id': self.item.pk,
			'periodo_id': self.periodo.pk,
		})
		self.assertEqual(response.status_code, 302)
		activity = Actividad.objects.get(descripcion_solicitud='Registro propio')
		self.assertEqual(activity.funcionario, self.officer_profile)

	def test_admin_can_update_officer_status_to_active(self):
		admin_user = User.objects.create_superuser(
			username='admin_estado',
			email='admin@example.test',
			password='test-pass',
		)
		self.officer_profile.estado = 'Inactivo'
		self.officer_profile.save()
		self.client.force_login(admin_user)

		response = self.client.post(
			reverse('gestion_funcionarios_editar', args=[self.officer_profile.pk]),
			{
				'identificador_institucional': self.officer_profile.identificador_institucional,
				'cargo_id': self.cargo.pk,
				'delegacion_id': self.centro.pk,
				'estado': 'Activo',
			},
		)

		self.assertEqual(response.status_code, 302)
		self.officer_profile.refresh_from_db()
		self.assertEqual(self.officer_profile.estado, 'Activo')

	def test_verifier_can_validate_evidence_without_edit_controls(self):
		self.client.force_login(self.verifier)
		response = self.client.get(reverse('gestion_actividades'))
		self.assertContains(response, 'Aprobar')
		self.assertNotContains(response, 'Actualizar Actividad')
		response = self.client.post(
			reverse('gestion_actividad_validar', args=[self.local_activity.pk]),
			{'resultado': 'Aprobado', 'observaciones': 'Evidencia conforme'},
		)
		self.assertEqual(response.status_code, 302)
		self.assertTrue(ValidacionEvidencia.objects.filter(
			actividad=self.local_activity,
			verificador=self.verifier_profile,
			resultado='Aprobado',
		).exists())

	def test_verifier_gets_validation_actions_and_readonly_activity_fields(self):
		request = RequestFactory().get('/admin/activities/actividad/')
		request.user = self.verifier
		model_admin = ActividadAdmin(Actividad, admin.site)

		actions = model_admin.get_actions(request)
		self.assertIn('aprobar_evidencias', actions)
		self.assertIn('rechazar_evidencias', actions)
		self.assertTrue(model_admin.has_change_permission(request))
		self.assertIn('updated_at', model_admin.get_list_display(request))
		self.assertIn('deleted_at', model_admin.get_list_display(request))
		self.assertIn('updated_at', model_admin.get_readonly_fields(request))
		self.assertIn('deleted_at', model_admin.get_readonly_fields(request))
		self.assertEqual(model_admin.get_inline_instances(request), [])

	def test_status_fields_use_select_choices(self):
		self.assertEqual(len(Delegacion._meta.get_field('estado').choices), 2)
		self.assertEqual(len(Funcionario._meta.get_field('estado').choices), 2)
		self.assertEqual(len(Periodo._meta.get_field('estado').choices), 2)
		self.assertEqual(len(CatalogoActividad._meta.get_field('estado').choices), 2)
		self.assertEqual(len(CompromisoAgenda._meta.get_field('estado').choices), 4)

	def test_agenda_custom_admin_action_updates_status(self):
		compromisso = CompromisoAgenda.objects.create(
			solicitante='Comunidad Centro',
			responsable=self.officer_profile,
			fecha_comprometida='2026-09-30',
		)
		request = RequestFactory().post('/admin/agenda/compromisoagenda/')
		request.user = self.delegate
		request.session = {}
		request._messages = FallbackStorage(request)
		model_admin = CompromisoAgendaAdmin(CompromisoAgenda, admin.site)

		model_admin.marcar_como_pendiente(request, CompromisoAgenda.objects.filter(pk=compromisso.pk))
		compromisso.refresh_from_db()
		self.assertEqual(compromisso.estado, 'Pendiente')
