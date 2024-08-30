from django.db import models

class Permission(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    permissions = models.ManyToManyField(Permission, related_name='roles')
    
    def __str__(self):
        return self.name
