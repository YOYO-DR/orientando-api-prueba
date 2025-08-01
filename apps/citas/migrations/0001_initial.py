# Generated by Django 5.2.4 on 2025-07-19 23:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora_inicio', models.DateTimeField(db_index=True)),
                ('fecha_hora_fin', models.DateTimeField(db_index=True)),
                ('google_calendar_event_id', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('google_calendar_url_event', models.CharField(blank=True, max_length=255, null=True)),
                ('observaciones', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Nombre descriptivo para la API Key', max_length=100)),
                ('key', models.CharField(editable=False, max_length=64, unique=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_used', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('usage_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('description', models.TextField(blank=True, help_text='Descripción del uso de esta API Key')),
            ],
            options={
                'verbose_name': 'API Key',
                'verbose_name_plural': 'API Keys',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['is_active', 'name'], name='apikey_active_name_idx'), models.Index(fields=['-created_at'], name='apikey_created_desc_idx'), models.Index(fields=['-last_used'], name='apikey_last_used_desc_idx'), models.Index(fields=['-usage_count'], name='apikey_usage_desc_idx')],
            },
        ),
        migrations.CreateModel(
            name='EstadoChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_whatsapp', models.CharField(max_length=20, unique=True)),
                ('estado_conversacion', models.JSONField()),
            ],
            options={
                'indexes': [models.Index(fields=['numero_whatsapp'], name='estadochat_whatsapp_idx')],
            },
        ),
        migrations.CreateModel(
            name='HistorialEstadoCita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado_cita', models.CharField(choices=[('Agendado', 'Agendado'), ('Notificado Profesional', 'Notificado Profesional'), ('Pendiente Primer Confirmación 24 Horas', 'Pendiente Primer Confirmación 24 Horas'), ('Primer Confirmado', 'Primer Confirmado'), ('Pendiente Segunda Confirmación 2 Horas', 'Pendiente Segunda Confirmación 2 Horas'), ('Segundo Confirmado', 'Segundo Confirmado'), ('Finalizado', 'Finalizado')], db_index=True, max_length=100)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('cita', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial_estados', to='citas.cita')),
            ],
        ),
        migrations.AddField(
            model_name='cita',
            name='estado_actual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cita_con_este_estado', to='citas.historialestadocita'),
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(db_index=True, max_length=255)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('es_agendable_por_bot', models.BooleanField(db_index=True, default=True)),
                ('duracion_minutos', models.PositiveIntegerField(db_index=True)),
            ],
            options={
                'indexes': [models.Index(fields=['es_agendable_por_bot', 'nombre'], name='producto_agendable_nombre_idx'), models.Index(fields=['duracion_minutos'], name='producto_duracion_idx')],
            },
        ),
        migrations.AddField(
            model_name='cita',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='citas.producto'),
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombres', models.CharField(db_index=True, max_length=255)),
                ('apellidos', models.CharField(db_index=True, max_length=255)),
                ('tipo_documento', models.CharField(choices=[('CC', 'Cédula de Ciudadanía'), ('TI', 'Tarjeta de Identidad'), ('NIT', 'NIT')], db_index=True, max_length=30)),
                ('numero_documento', models.CharField(max_length=100, unique=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True, unique=True)),
                ('celular', models.CharField(db_index=True, max_length=20)),
                ('tipo', models.CharField(choices=[('Cliente', 'Cliente'), ('Profesional', 'Profesional')], db_index=True, max_length=20)),
            ],
            options={
                'indexes': [models.Index(fields=['nombres', 'apellidos'], name='usuario_nombre_completo_idx'), models.Index(fields=['tipo', 'nombres'], name='usuario_tipo_nombre_idx'), models.Index(fields=['tipo_documento', 'numero_documento'], name='usuario_documento_idx')],
            },
        ),
        migrations.CreateModel(
            name='Profesional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_whatsapp', models.CharField(max_length=20, unique=True)),
                ('cargo', models.CharField(blank=True, db_index=True, max_length=150, null=True)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='citas.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='ProductoProfesional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='citas.producto')),
                ('profesional', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='citas.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_acudiente', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('edad', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('barrio', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('direccion', models.CharField(blank=True, max_length=255, null=True)),
                ('remitido_colegio', models.BooleanField(blank=True, db_index=True, default=False, null=True)),
                ('colegio', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('estado_chat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='citas.estadochat')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='citas.usuario')),
            ],
        ),
        migrations.AddField(
            model_name='cita',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='citas', to='citas.usuario'),
        ),
        migrations.AddField(
            model_name='cita',
            name='profesional_asignado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='citas_asignadas', to='citas.usuario'),
        ),
        migrations.AddIndex(
            model_name='historialestadocita',
            index=models.Index(fields=['cita', 'fecha_registro'], name='historial_cita_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='historialestadocita',
            index=models.Index(fields=['estado_cita', 'fecha_registro'], name='historial_estado_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='historialestadocita',
            index=models.Index(fields=['-fecha_registro'], name='historial_fecha_desc_idx'),
        ),
        migrations.AddIndex(
            model_name='profesional',
            index=models.Index(fields=['cargo'], name='profesional_cargo_idx'),
        ),
        migrations.AddIndex(
            model_name='profesional',
            index=models.Index(fields=['numero_whatsapp'], name='profesional_whatsapp_idx'),
        ),
        migrations.AddIndex(
            model_name='productoprofesional',
            index=models.Index(fields=['producto', 'profesional'], name='producto_profesional_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='productoprofesional',
            unique_together={('producto', 'profesional')},
        ),
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['remitido_colegio', 'colegio'], name='cliente_colegio_idx'),
        ),
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['barrio'], name='cliente_barrio_idx'),
        ),
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['edad'], name='cliente_edad_idx'),
        ),
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['estado_chat'], name='cliente_estado_chat_idx'),
        ),
        migrations.AddIndex(
            model_name='cita',
            index=models.Index(fields=['fecha_hora_inicio', 'fecha_hora_fin'], name='cita_horario_idx'),
        ),
        migrations.AddIndex(
            model_name='cita',
            index=models.Index(fields=['cliente', 'fecha_hora_inicio'], name='cita_cliente_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='cita',
            index=models.Index(fields=['profesional_asignado', 'fecha_hora_inicio'], name='cita_profesional_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='cita',
            index=models.Index(fields=['producto', 'fecha_hora_inicio'], name='cita_producto_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='cita',
            index=models.Index(fields=['estado_actual', 'fecha_hora_inicio'], name='cita_estado_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='cita',
            index=models.Index(fields=['-fecha_hora_inicio'], name='cita_fecha_desc_idx'),
        ),
        migrations.AddIndex(
            model_name='cita',
            index=models.Index(fields=['google_calendar_event_id'], name='cita_calendar_event_idx'),
        ),
    ]
