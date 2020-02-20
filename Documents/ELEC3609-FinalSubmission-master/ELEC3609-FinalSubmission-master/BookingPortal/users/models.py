from django.db import models
from django.contrib.auth.models import User
from PIL import Image

# Profile model extends User model through OneToOneField
# Necessary to store additonal data - image and user type
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    userType = models.TextField(choices=(
        ('User',('User Account')),
        ('Business', ('Business Account')),
    )
    ,default='User')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.image.path)

