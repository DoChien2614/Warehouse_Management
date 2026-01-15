from django.contrib.auth.models import User
user = User.objects.create_superuser('admin', 'your-email@example.com', 'password123')
user.save()
