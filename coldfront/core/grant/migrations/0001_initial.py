# Generated by Django 2.2.3 on 2019-07-18 18:51

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrantFundingAgency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GrantStatusChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='HistoricalGrant',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(255)])),
                ('grant_number', models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(255)], verbose_name='Grant Number from funding agency')),
                ('role', models.CharField(choices=[('PI', 'Principal Investigator (PI)'), ('CoPI', 'Co-Principal Investigator (CoPI)'), ('SP', 'Senior Personnel (SP)')], max_length=10)),
                ('grant_pi_full_name', models.CharField(blank=True, max_length=255, verbose_name='Grant PI Full Name')),
                ('other_funding_agency', models.CharField(blank=True, max_length=255)),
                ('other_award_number', models.CharField(blank=True, max_length=255)),
                ('grant_start', models.DateField(verbose_name='Grant Start Date')),
                ('grant_end', models.DateField(verbose_name='Grant End Date')),
                ('percent_credit', models.FloatField(validators=[django.core.validators.MaxValueValidator(100)])),
                ('direct_funding', models.FloatField()),
                ('total_amount_awarded', models.CharField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('funding_agency', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='grant.GrantFundingAgency')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='project.Project')),
                ('status', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='grant.GrantStatusChoice')),
            ],
            options={
                'verbose_name': 'historical grant',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(255)])),
                ('grant_number', models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(255)], verbose_name='Grant Number from funding agency')),
                ('role', models.CharField(choices=[('PI', 'Principal Investigator (PI)'), ('CoPI', 'Co-Principal Investigator (CoPI)'), ('SP', 'Senior Personnel (SP)')], max_length=10)),
                ('grant_pi_full_name', models.CharField(blank=True, max_length=255, verbose_name='Grant PI Full Name')),
                ('other_funding_agency', models.CharField(blank=True, max_length=255)),
                ('other_award_number', models.CharField(blank=True, max_length=255)),
                ('grant_start', models.DateField(verbose_name='Grant Start Date')),
                ('grant_end', models.DateField(verbose_name='Grant End Date')),
                ('percent_credit', models.FloatField(validators=[django.core.validators.MaxValueValidator(100)])),
                ('direct_funding', models.FloatField()),
                ('total_amount_awarded', models.FloatField()),
                ('funding_agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grant.GrantFundingAgency')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grant.GrantStatusChoice')),
            ],
            options={
                'verbose_name_plural': 'Grants',
                'permissions': (('can_view_all_grants', 'Can view all grants'),),
            },
        ),
    ]
