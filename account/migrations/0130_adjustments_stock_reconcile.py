from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0129_notifications_analog_readings_used'),
    ]

    operations = [
        migrations.AddField(
            model_name='adjustments',
            name='stock_reconcile',
            field=models.BooleanField(default=False),
        ),
    ]
