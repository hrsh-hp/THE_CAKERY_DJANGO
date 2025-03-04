from django.conf import settings
from django.db import models

from Auth.models import CustomUser
from helpers import generate_unique_hash

# Create your models here.
class Cake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to='images/cakes/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    available_toppings = models.BooleanField(default=True)
    slug = models.SlugField(unique=True,null=True,blank=True)

    def __str__(self):
        return self.name
    
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Cake, self).save(*args, **kwargs)

    def image_url(self):
        """Return full image URL"""
        if self.image:
            return f"{settings.MEDIA_URL}{self.image.name}"
        return None
    
class CakeSize(models.Model):
    cake = models.ForeignKey(Cake,on_delete=models.CASCADE,related_name='sizes')
    size = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(unique=True,null=True,blank=True)

    def __str__(self):
        return f"{self.size} - {self.price}"
    
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(CakeSize, self).save(*args, **kwargs)

class CakeLike(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cake = models.ForeignKey(Cake, related_name="likes", on_delete=models.CASCADE)
    liked = models.BooleanField(default=True)  # True if liked, False if unliked

    class Meta:
        unique_together = ('user', 'cake')  # user can like a cake only once

    def __str__(self):
        return f"{self.user.email} {'liked' if self.liked else 'unliked'} {self.cake.name}"
    