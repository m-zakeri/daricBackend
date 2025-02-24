# Generated by Django 5.1.5 on 2025-02-24 20:48

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daric', '0004_remove_transaction_transactiontype'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, help_text='The date and time when the user was created.', verbose_name='Created At'),
            preserve_default=False,
        ),
    ]
