from django.db import migrations

def create_initial_hr_account(apps, schema_editor):
    HRAccount = apps.get_model('hrms', 'HRAccount')
    HRAccount.objects.create(
        email='hr@example.com',
        password='password123'  # Use hashed passwords in practice
    )

class Migration(migrations.Migration):
    dependencies = [
        ('hrms', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_hr_account),
    ]
