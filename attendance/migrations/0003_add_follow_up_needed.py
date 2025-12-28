from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_weeklyattendance'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitorrecord',
            name='follow_up_needed',
            field=models.BooleanField(default=True),
        ),
    ]
