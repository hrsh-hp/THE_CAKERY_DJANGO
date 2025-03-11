from django.contrib import admin
from .models import CustomUser,Address,DeliveryPerson
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Address)
admin.site.register(DeliveryPerson)