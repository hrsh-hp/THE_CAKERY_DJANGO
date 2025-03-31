from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator,MinValueValidator

from Auth.managers import UserManager
from helpers import generate_unique_hash


# Create your models here.
ROLES = [('user','User'),('admin','Admin'),('delivery_person','Delivery Person')]
class CustomUser(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    username = None
    # name = models.CharField(max_length=255,null=True,blank=True)
    email = models.EmailField(unique=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    user_image = models.ImageField(upload_to = 'images/user/',null=True, blank=True)
    phone_no = models.BigIntegerField(validators=[MaxValueValidator(999999999999),MinValueValidator(000000000000)],null=True, blank=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=255,choices=ROLES,default='user')

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

    def image_url(self):
        """Return full image URL"""
        if self.image:
            return f"{settings.MEDIA_URL}{self.image.name}"
        return None


class Address(models.Model):
    address_text = models.TextField()
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='address_set')
    longitude = models.CharField(max_length=255,null=True,blank=True)
    latitude = models.CharField(max_length=255,null=True,blank=True)
    slug = models.SlugField(unique=True,null=True,blank=True)

    def __str__(self):
        return self.user.email + "'s address"
    
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Address, self).save(*args, **kwargs)

class DeliveryPerson(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="delivery_profile")
    vehicle_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    assigned_orders = models.ManyToManyField("cakes.Order", related_name="assigned_delivery", blank=True)
    slug = models.SlugField(unique=True,null=True,blank=True)

    def __str__(self):
        return f"Delivery Person - {self.user.email}"
    
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(DeliveryPerson, self).save(*args, **kwargs)