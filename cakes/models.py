from django.conf import settings
from django.db import models

from Auth.models import CustomUser
from helpers import generate_unique_hash


class Topping(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(unique=True,null=True,blank=True)

    def __str__(self):
        return f"{self.name} - ₹{self.price}"
    
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Topping, self).save(*args, **kwargs)
    
class Cake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    # price = models.FloatField()
    image = models.ImageField(upload_to='images/cakes/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    available_toppings = models.BooleanField(default=True)
    toppings = models.ManyToManyField(Topping, blank=True)
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
    liked = models.BooleanField(default=True)  

    class Meta:
        unique_together = ('user', 'cake')  

    def __str__(self):
        return f"{self.user.email} {'liked' if self.liked else 'unliked'} {self.cake.name}"

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='carts')
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {'Paid' if self.is_paid else 'Active'} Cart"
    
    def get_cart_total(self):
        cart_items = CartItems.objects.filter(cart__is_paid=False,cart=self)
    
        return sum(cart_item.size.price * cart_item.quantity for cart_item in cart_items)
    
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Cart, self).save(*args, **kwargs)
    
    @staticmethod
    def get_or_create_active_cart(user):
        """
        Ensure that a user has only one active cart.
        If no active cart exists, create a new one.
        """
        cart, created = Cart.objects.get_or_create(user=user, is_paid=False)
        return cart

class CartItems(models.Model):
    cart = models.ForeignKey(Cart , on_delete=models.CASCADE, related_name="cart_items")
    cake = models.ForeignKey(Cake,  on_delete=models.CASCADE)
    size = models.ForeignKey(CakeSize, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    toppings = toppings = models.ManyToManyField(Topping, blank=True)
    

    def __str__(self) -> str:
        if self.cake:
            return f"{self.cart.user.email} - cart item - {self.quantity}x {self.cake.name} ({self.size.size})"
        else:
            return f"{self.cart.user.email} - cart item - None"
    
    def get_item_price(self):
        if self.cake:
            base_price = self.size.price
            toppings_price = sum(t.price for t in self.toppings.all())
            return (base_price + toppings_price) * self.quantity
        