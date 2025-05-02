from django.contrib import admin
from core.models import User, Role, Account, Destination, Log

# Register your models here.




class DestinationAdmin(admin.ModelAdmin):
    list_display = ('account', 'url', 'http_method', 'created_at', 'updated_at')

# Registering each model
admin.site.register(User)
admin.site.register(Role)
admin.site.register(Account)
admin.site.register(Destination)
admin.site.register(Log)