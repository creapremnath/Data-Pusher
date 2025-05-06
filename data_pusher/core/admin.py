from django.contrib import admin
from core.models import User, Role, Account, Destination, Log, AccountMember

# Register your models here

# Registering each model
admin.site.register(User)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_id', 'role_name')


admin.site.register(Account)
admin.site.register(AccountMember)

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('destination_id', 'account_id', 'url', 'http_method', 'created_at', 'updated_at')
    search_fields = ['url', 'http_method']
    list_filter = ['http_method', 'account_id']
    ordering = ['created_at']


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'account_id', 'get_destination', 'status', 'received_timestamp', 'processed_timestamp')
    search_fields = ['event_id', 'status']
    list_filter = ['status', 'received_timestamp']
    ordering = ['received_timestamp']

    # Custom method to display destination-related information
    def get_destination(self, obj):
        return obj.destination_id.url  # Access the related destination via 'destination_id'
    get_destination.short_description = 'Destination URL'  # Optional: Set a custom label for this field
