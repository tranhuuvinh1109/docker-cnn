# Generated by Django 4.2.5 on 2023-10-02 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_remove_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='default username', max_length=255, unique=True),
        ),
    ]