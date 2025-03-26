from django.contrib import admin
from cakes.models import Cake,CakeSize,CakeLike,Cart,CartItems,Topping,Order,Payment,Review,CakeSponge

# Register your models here.
admin.site.register(Cake)
admin.site.register(CakeSize)
admin.site.register(CakeLike)
admin.site.register(CakeSponge)
admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(Topping)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Review)