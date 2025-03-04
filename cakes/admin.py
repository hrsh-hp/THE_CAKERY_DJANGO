from django.contrib import admin
from cakes.models import Cake,CakeSize,CakeLike

# Register your models here.
admin.site.register(Cake)
admin.site.register(CakeSize)
admin.site.register(CakeLike)