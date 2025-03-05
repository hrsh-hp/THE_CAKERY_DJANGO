from django.contrib import admin
from cakes.models import Cake,CakeSize,CakeLike,Cart,CartItems

# Register your models here.
admin.site.register(Cake)
admin.site.register(CakeSize)
admin.site.register(CakeLike)
admin.site.register(Cart)
admin.site.register(CartItems)