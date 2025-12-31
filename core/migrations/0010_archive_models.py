# Generated migration for archive models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_remove_calendarevent_color_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinancialArchive',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
                ('archive_date', models.DateTimeField(auto_now_add=True)),
                ('data_summary', models.JSONField(default=dict, help_text='Summary of archived data')),
                ('mission_total_contributions', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('mission_total_expenditures', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('mission_total_tithes', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('mission_total_offerings', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('branch_count', models.IntegerField(default=0)),
                ('total_branch_contributions', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('total_branch_expenditures', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('total_pastor_commissions', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('commissions_paid', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('commissions_pending', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('fiscal_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='archives', to='core.fiscalyear')),
            ],
            options={
                'verbose_name': 'Financial Archive',
                'verbose_name_plural': 'Financial Archives',
            },
        ),
        migrations.CreateModel(
            name='MemberArchive',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
                ('archive_date', models.DateTimeField(auto_now_add=True)),
                ('data_summary', models.JSONField(default=dict, help_text='Summary of archived data')),
                ('total_members', models.IntegerField(default=0)),
                ('new_members', models.IntegerField(default=0)),
                ('transferred_members', models.IntegerField(default=0)),
                ('inactive_members', models.IntegerField(default=0)),
                ('total_services', models.IntegerField(default=0)),
                ('average_attendance', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('highest_attendance', models.IntegerField(default=0)),
                ('lowest_attendance', models.IntegerField(default=0)),
                ('members_by_branch', models.JSONField(default=dict, help_text='Member count by branch')),
                ('members_by_area', models.JSONField(default=dict, help_text='Member count by area')),
                ('members_by_district', models.JSONField(default=dict, help_text='Member count by district')),
                ('fiscal_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_archives', to='core.fiscalyear')),
            ],
            options={
                'verbose_name': 'Member Archive',
                'verbose_name_plural': 'Member Archives',
            },
        ),
        migrations.CreateModel(
            name='BranchArchive',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
                ('archive_date', models.DateTimeField(auto_now_add=True)),
                ('data_summary', models.JSONField(default=dict, help_text='Summary of archived data')),
                ('total_contributions', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('total_tithes', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('total_offerings', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('total_expenditures', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('member_count', models.IntegerField(default=0)),
                ('new_members', models.IntegerField(default=0)),
                ('average_attendance', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('pastor_name', models.CharField(blank=True, max_length=200)),
                ('pastor_commission_earned', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('pastor_commission_paid', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('tithe_target_achievement', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('growth_percentage', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yearly_archives', to='core.branch')),
                ('fiscal_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branch_archives', to='core.fiscalyear')),
            ],
            options={
                'verbose_name': 'Branch Archive',
                'verbose_name_plural': 'Branch Archives',
            },
        ),
        migrations.AlterUniqueTogether(
            name='financialarchive',
            unique_together={('fiscal_year',)},
        ),
        migrations.AlterUniqueTogether(
            name='memberarchive',
            unique_together={('fiscal_year',)},
        ),
        migrations.AlterUniqueTogether(
            name='brancharchive',
            unique_together={('fiscal_year', 'branch')},
        ),
    ]
