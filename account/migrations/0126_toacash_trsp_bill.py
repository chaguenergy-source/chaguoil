from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0125_loanpayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='toacash',
            name='trsp_bill',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.transporter'),
        ),
    ]
