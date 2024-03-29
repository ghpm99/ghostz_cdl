# Generated by Django 4.1.5 on 2023-01-13 02:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Overlay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.TextField()),
                ('hour', models.TextField()),
                ('modality', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('twitch', models.TextField()),
                ('mmr', models.TextField()),
                ('mmr_as', models.TextField()),
                ('overlay', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='overlay.overlay')),
            ],
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family', models.TextField()),
                ('name', models.TextField()),
                ('bdo_class', models.TextField()),
                ('combat_style', models.TextField()),
                ('matches', models.TextField()),
                ('defeats', models.TextField()),
                ('victories', models.TextField()),
                ('champion', models.TextField()),
                ('dr', models.TextField()),
                ('by', models.TextField()),
                ('walkover', models.TextField()),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='overlay.team')),
            ],
        ),
    ]
