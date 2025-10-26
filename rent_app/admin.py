from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Tenant, RentAgreement, RentPayment, UtilityType, UtilityBill,
    MeterType, MeterReading, SystemSettings
)


class TenantInline(admin.StackedInline):
    model = Tenant
    can_delete = False
    verbose_name_plural = 'Tenant Profile'


class CustomUserAdmin(UserAdmin):
    inlines = (TenantInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'has_tenant_profile')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    def has_tenant_profile(self, obj):
        return hasattr(obj, 'tenant')
    has_tenant_profile.boolean = True
    has_tenant_profile.short_description = 'Has Tenant Profile'


# Unregister the default User admin
admin.site.unregister(User)

# Register the custom User admin
admin.site.register(User, CustomUserAdmin)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_full_name', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    ordering = ['-created_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def save_model(self, request, obj, form, change):
        # Ensure the associated user is active and not a superuser
        if obj.user:
            obj.user.is_staff = False
            obj.user.is_superuser = False
            obj.user.save()
        super().save_model(request, obj, form, change)


@admin.register(RentAgreement)
class RentAgreementAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'monthly_rent_eur', 'monthly_rent_ron', 'start_date', 'is_active']
    list_filter = ['is_active', 'start_date']
    search_fields = ['tenant__user__username', 'tenant__user__first_name']
    ordering = ['-start_date']


@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):
    list_display = ['agreement', 'amount_eur', 'amount_ron', 'due_date', 'status', 'payment_date']
    list_filter = ['status', 'due_date', 'payment_date']
    search_fields = ['agreement__tenant__user__username']
    ordering = ['-due_date']


@admin.register(UtilityType)
class UtilityTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(UtilityBill)
class UtilityBillAdmin(admin.ModelAdmin):
    list_display = ['utility_type', 'tenant', 'amount', 'invoice_number', 'due_date', 'status', 'paid_on']
    list_filter = ['status', 'due_date', 'paid_on', 'utility_type', 'tenant']
    search_fields = ['tenant__user__username', 'utility_type__name', 'invoice_number']
    ordering = ['-due_date']

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # Reorder fields for better UX
        if obj is None:  # For add form
            return ['utility_type', 'tenant', 'amount', 'invoice_number', 'due_date', 'bill_date', 'status', 'paid_on', 'bill_file', 'notes']
        return fields


@admin.register(MeterType)
class MeterTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'reading_day_start', 'reading_day_end', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'unit']
    ordering = ['name']


@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    list_display = ['meter_type', 'tenant', 'reading_value', 'reading_date', 'is_processed']
    list_filter = ['is_processed', 'reading_date', 'meter_type']
    search_fields = ['tenant__user__username', 'meter_type__name']
    ordering = ['-reading_date']


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'updated_at']
    search_fields = ['key', 'description']
    ordering = ['key']
