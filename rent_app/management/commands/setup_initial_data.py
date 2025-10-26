from django.core.management.base import BaseCommand
from rent_app.models import UtilityType, MeterType, SystemSettings


class Command(BaseCommand):
    help = 'Set up initial data for the rent manager application'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')

        # Create utility types
        utility_types = [
            {'name': 'Electricity', 'description': 'Electricity bills'},
            {'name': 'Gas', 'description': 'Natural gas bills'},
            {'name': 'Water', 'description': 'Water and sewage bills'},
            {'name': 'Internet', 'description': 'Internet service bills'},
            {'name': 'Condominio', 'description': 'Condominium maintenance fees'},
        ]

        for utility_data in utility_types:
            utility_type, created = UtilityType.objects.get_or_create(
                name=utility_data['name'],
                defaults=utility_data
            )
            if created:
                self.stdout.write(f'Created utility type: {utility_type.name}')
            else:
                self.stdout.write(f'Utility type already exists: {utility_type.name}')

        # Create meter types with reading periods
        meter_types = [
            {
                'name': 'Electricity',
                'unit': 'kWh',
                'reading_day_start': 25,
                'reading_day_end': 5,
            },
            {
                'name': 'Gas',
                'unit': 'm³',
                'reading_day_start': 20,
                'reading_day_end': 10,
            },
            {
                'name': 'Water',
                'unit': 'm³',
                'reading_day_start': 15,
                'reading_day_end': 5,
            },
        ]

        for meter_data in meter_types:
            meter_type, created = MeterType.objects.get_or_create(
                name=meter_data['name'],
                defaults=meter_data
            )
            if created:
                self.stdout.write(f'Created meter type: {meter_type.name} ({meter_type.reading_day_start}-{meter_type.reading_day_end})')
            else:
                self.stdout.write(f'Meter type already exists: {meter_type.name}')

        # Create system settings
        system_settings = [
            {
                'key': 'bnr_exchange_rate_url',
                'value': 'https://www.bnr.ro/nbrfxrates.xml',
                'description': 'BNR XML feed URL for exchange rates'
            },
            {
                'key': 'default_exchange_rate',
                'value': '5.00',
                'description': 'Default EUR to RON exchange rate when BNR is unavailable'
            },
            {
                'key': 'meter_reading_notification_days',
                'value': '3',
                'description': 'Days before reading period ends to send notification'
            },
        ]

        for setting_data in system_settings:
            setting, created = SystemSettings.objects.get_or_create(
                key=setting_data['key'],
                defaults=setting_data
            )
            if created:
                self.stdout.write(f'Created system setting: {setting.key}')
            else:
                self.stdout.write(f'System setting already exists: {setting.key}')

        self.stdout.write(self.style.SUCCESS('Initial data setup completed!'))
