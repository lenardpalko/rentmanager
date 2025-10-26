from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import requests

from .models import (
    Tenant, RentAgreement, RentPayment, UtilityType, UtilityBill,
    MeterType, MeterReading, SystemSettings
)


@login_required
def dashboard(request):
    """Main dashboard view"""
    # Check if user is admin (superuser) and redirect to admin interface
    if request.user.is_superuser:
        return redirect('/admin/')

    # For regular tenants
    tenant = get_object_or_404(Tenant, user=request.user)

    # Get recent rent payments
    rent_agreement = RentAgreement.objects.filter(tenant=tenant, is_active=True).first()
    recent_payments = []
    if rent_agreement:
        recent_payments = RentPayment.objects.filter(
            agreement=rent_agreement
        ).order_by('-due_date')[:5]

    # Get pending bills count (all unpaid and overdue bills)
    pending_bills_count = UtilityBill.objects.filter(
        tenant=tenant,
        status__in=['unpaid', 'overdue']
    ).count()

    # Get bills to pay (unpaid and overdue, ordered by due date)
    upcoming_bills = UtilityBill.objects.filter(
        tenant=tenant,
        status__in=['unpaid', 'overdue']
    ).order_by('due_date')[:5]

    # Get recent meter readings
    recent_readings = MeterReading.objects.filter(
        tenant=tenant
    ).order_by('-reading_date')[:3]

    context = {
        'tenant': tenant,
        'rent_agreement': rent_agreement,
        'recent_payments': recent_payments,
        'pending_bills_count': pending_bills_count,
        'upcoming_bills': upcoming_bills,
        'recent_readings': recent_readings,
    }

    return render(request, 'rent_app/dashboard.html', context)


@login_required
def rent_status(request):
    """Rent status and payment history"""
    # Admin users should not access tenant pages
    if request.user.is_superuser:
        return redirect('/admin/')

    tenant = get_object_or_404(Tenant, user=request.user)
    rent_agreement = get_object_or_404(RentAgreement, tenant=tenant, is_active=True)

    # Get current month payment
    current_date = timezone.now().date()
    current_month_payment = RentPayment.objects.filter(
        agreement=rent_agreement,
        due_date__year=current_date.year,
        due_date__month=current_date.month
    ).first()

    # Get all payments
    all_payments = RentPayment.objects.filter(
        agreement=rent_agreement
    ).order_by('-due_date')

    context = {
        'rent_agreement': rent_agreement,
        'current_month_payment': current_month_payment,
        'all_payments': all_payments,
        'current_date': current_date,
    }

    return render(request, 'rent_app/rent_status.html', context)


@login_required
def utility_bills(request):
    """Utility bills view"""
    # Admin users should not access tenant pages
    if request.user.is_superuser:
        return redirect('/admin/')

    tenant = get_object_or_404(Tenant, user=request.user)

    # Get bills by status
    unpaid_bills = UtilityBill.objects.filter(
        tenant=tenant,
        status='unpaid'
    ).order_by('due_date')

    paid_bills = UtilityBill.objects.filter(
        tenant=tenant,
        status='paid'
    ).order_by('-due_date')[:10]  # Last 10 paid bills

    overdue_bills = UtilityBill.objects.filter(
        tenant=tenant,
        status='overdue'
    ).order_by('due_date')

    context = {
        'unpaid_bills': unpaid_bills,
        'paid_bills': paid_bills,
        'overdue_bills': overdue_bills,
    }

    return render(request, 'rent_app/utility_bills.html', context)


@login_required
def download_bill(request, bill_id):
    """Download utility bill file"""
    # Admin users should not access tenant pages
    if request.user.is_superuser:
        return redirect('/admin/')

    tenant = get_object_or_404(Tenant, user=request.user)
    bill = get_object_or_404(UtilityBill, id=bill_id, tenant=tenant)

    if not bill.bill_file:
        messages.error(request, "No file attached to this bill.")
        return redirect('rent_app:utility_bills')

    # Return the file
    response = HttpResponse(bill.bill_file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{bill.utility_type.name}_{bill.due_date}.pdf"'
    return response


@login_required
def meter_readings(request):
    """Meter readings view"""
    # Admin users should not access tenant pages
    if request.user.is_superuser:
        return redirect('/admin/')

    tenant = get_object_or_404(Tenant, user=request.user)

    # Get all meter types
    meter_types = MeterType.objects.filter(is_active=True)

    # Create meter data with latest readings
    meter_data = []
    for meter_type in meter_types:
        latest_reading = MeterReading.objects.filter(
            tenant=tenant,
            meter_type=meter_type
        ).order_by('-reading_date').first()

        meter_data.append({
            'meter_type': meter_type,
            'latest_reading': latest_reading,
        })

    # Check if any meter is in reading period
    current_date = timezone.now().date()
    current_day = current_date.day

    meters_in_period = []
    for meter_type in meter_types:
        in_period = (meter_type.reading_day_start <= current_day <= meter_type.reading_day_end)
        if in_period:
            meters_in_period.append(meter_type)

    context = {
        'meter_data': meter_data,
        'meters_in_period': meters_in_period,
        'current_date': current_date,
    }

    return render(request, 'rent_app/meter_readings.html', context)


@login_required
def submit_meter_reading(request):
    """Submit a new meter reading"""
    # Admin users should not access tenant pages
    if request.user.is_superuser:
        return redirect('/admin/')

    if request.method == 'POST':
        tenant = get_object_or_404(Tenant, user=request.user)
        meter_type_id = request.POST.get('meter_type')
        reading_value = request.POST.get('reading_value')
        notes = request.POST.get('notes', '')

        try:
            meter_type = MeterType.objects.get(id=meter_type_id, is_active=True)
            reading_date = timezone.now().date()

            # Check if reading already exists for today
            existing_reading = MeterReading.objects.filter(
                tenant=tenant,
                meter_type=meter_type,
                reading_date=reading_date
            ).exists()

            if existing_reading:
                messages.error(request, f"You have already submitted a {meter_type.name} reading today.")
                return redirect('rent_app:meter_readings')

            # Create new reading
            MeterReading.objects.create(
                tenant=tenant,
                meter_type=meter_type,
                reading_value=reading_value,
                reading_date=reading_date,
                notes=notes
            )

            messages.success(request, f"{meter_type.name} reading submitted successfully!")

            # Send notification email to admin
            try:
                send_mail(
                    subject=f'New Meter Reading Submitted - {meter_type.name}',
                    message=f'Tenant {tenant.user.get_full_name()} has submitted a new {meter_type.name} reading: {reading_value} {meter_type.unit}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMINS[0][1] if settings.ADMINS else 'admin@rentmanager.palko.app'],
                    fail_silently=True,
                )
            except:
                pass  # Email failure shouldn't break the flow

        except MeterType.DoesNotExist:
            messages.error(request, "Invalid meter type selected.")
        except ValueError:
            messages.error(request, "Invalid reading value.")

    return redirect('rent_app:meter_readings')
