from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator,MinValueValidator

from Auth.managers import UserManager
from helpers import generate_unique_hash


# Create your models here.
class CustomUser(AbstractUser):
    username = None
    name = models.CharField(max_length=255,null=True,blank=True)
    email = models.EmailField(unique=True)
    ph_no = models.CharField(max_length=20,null=True,blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    phone_no = models.IntegerField(validators=[MaxValueValidator(999999999999),MinValueValidator(000000000000)],null=True, blank=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __name__(self):
        return self.name
    
    def __str__(self):
        return self.email
    
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(CustomUser, self).save(*args, **kwargs)


class Address(models.Model):
    address_text = models.TextField()
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    longitude = models.CharField(max_length=255,null=True,blank=True)
    latitude = models.CharField(max_length=255,null=True,blank=True)
    slug = models.SlugField(unique=True,null=True,blank=True)

    def __str__(self):
        return self.user.email + "'s address"
    
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Address, self).save(*args, **kwargs)
