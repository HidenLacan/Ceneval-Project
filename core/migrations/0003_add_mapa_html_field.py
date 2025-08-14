# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_configuracionruta'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionruta',
            name='mapa_html',
            field=models.TextField(blank=True, null=True, verbose_name='HTML completo del mapa para renderizar'),
        ),
    ] 