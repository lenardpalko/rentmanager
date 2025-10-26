from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator


class Tenant(models.Model):
    """Tenant model - represents the renter"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"


class RentAgreement(models.Model):
    """Rent agreement with tenant"""
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    monthly_rent_eur = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rent Agreement for {self.tenant}"

    @property
    def monthly_rent_ron(self):
        """Convert EUR to RON using current BNR rate"""
        # For now, return EUR * 5 as a placeholder
        # TODO: Implement actual BNR API integration
        return self.monthly_rent_eur * 5


class RentPayment(models.Model):
    """Rent payment records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    agreement = models.ForeignKey(RentAgreement, on_delete=models.CASCADE)
    amount_ron = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    amount_eur = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    exchange_rate = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        validators=[MinValueValidator(0)]
    )
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rent Payment {self.amount_eur} EUR ({self.amount_ron} RON) - {self.due_date}"

    class Meta:
        ordering = ['-due_date']


class UtilityType(models.Model):
    """Types of utilities (electricity, gas, water, internet, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Utility Type"
        verbose_name_plural = "Utility Types"


class UtilityBill(models.Model):
    """Utility bills that need to be paid"""
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    utility_type = models.ForeignKey(UtilityType, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    due_date = models.DateField()
    bill_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    bill_file = models.FileField(upload_to='utility_bills/', blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, help_text="Optional invoice number")
    paid_on = models.DateField(null=True, blank=True, help_text="Date when the bill was paid")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.utility_type.name} - {self.amount} RON - Due: {self.due_date}"

    class Meta:
        ordering = ['-due_date']


class MeterType(models.Model):
    """Types of meters (electricity, gas, water)"""
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=20, help_text="Unit of measurement (kWh, m³, etc.)")
    reading_day_start = models.PositiveIntegerField(
        help_text="Day of month when reading period starts (1-31)"
    )
    reading_day_end = models.PositiveIntegerField(
        help_text="Day of month when reading period ends (1-31)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.reading_day_start}-{self.reading_day_end})"

    class Meta:
        verbose_name = "Meter Type"
        verbose_name_plural = "Meter Types"


class MeterReading(models.Model):
    """Meter readings submitted by tenants"""
    meter_type = models.ForeignKey(MeterType, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    reading_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    reading_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.meter_type.name}: {self.reading_value} {self.meter_type.unit} - {self.reading_date}"

    class Meta:
        ordering = ['-reading_date']
        unique_together = ['meter_type', 'tenant', 'reading_date']


class SystemSettings(models.Model):
    """System-wide settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"
