# Rent Manager

A Django-based application for managing apartment rentals, utility bills, and meter readings.

## Features

- **Authentication**: User login with password change capability
- **Rent Management**: Track rent payments in EUR with RON conversion using BNR rates
- **Utility Bills**: Upload and manage utility bills (electricity, gas, water, internet, condominio)
- **Meter Readings**: Monthly meter readings with configurable reading periods
- **Email Notifications**: Automated notifications for meter reading periods and submissions
- **Admin Interface**: Comprehensive admin panel for managing tenants, bills, and settings

## Setup

1. **Clone and install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server**:
   ```bash
   python manage.py runserver
   ```

## Deployment

This application is configured for deployment with Docker similar to the family_bank app:

```bash
docker-compose up -d
```

## Environment Variables

### Required
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `CSRF_TRUSTED_ORIGINS`: Comma-separated list of trusted origins

### Required for Production
- **Cloudflare R2 Storage** (for file uploads):
  - `R2_ACCESS_KEY_ID` - Your R2 API access key ID
  - `R2_SECRET_ACCESS_KEY` - Your R2 API secret access key
  - `R2_BUCKET_NAME` - Your R2 bucket name
  - `R2_ENDPOINT_URL` - Your R2 endpoint URL (https://your-account-id.r2.cloudflarestorage.com)
  - `R2_REGION_NAME` - Set to "auto" for R2
  - `R2_CUSTOM_DOMAIN` - Optional custom domain for serving files

### Optional (but recommended)

- **Email (SendGrid)**:
  - `EMAIL_HOST=smtp.sendgrid.net`
  - `EMAIL_PORT=587`
  - `EMAIL_USE_TLS=True`
  - `EMAIL_HOST_USER=apikey`
  - `EMAIL_HOST_PASSWORD=your-sendgrid-api-key`
  - `DEFAULT_FROM_EMAIL=noreply@rentmanager.palko.app`

## Cloudflare R2 Setup

For production deployment, you need to configure Cloudflare R2 for file storage:

1. **Create R2 Bucket**:
   - Go to Cloudflare Dashboard → R2 Object Storage
   - Create a new bucket
   - Note the bucket name

2. **Create API Token**:
   - Go to R2 → Manage R2 API tokens
   - Create a new API token with appropriate permissions
   - Note the Access Key ID and Secret Access Key

3. **Get Endpoint URL**:
   - Your endpoint URL format: `https://your-account-id.r2.cloudflarestorage.com`
   - Find your account ID in Cloudflare Dashboard → Right sidebar

4. **Configure Environment**:
   - Update your `.env` file with the R2 credentials:
     ```env
     R2_ACCESS_KEY_ID=your-r2-access-key-id
     R2_SECRET_ACCESS_KEY=your-r2-secret-access-key
     R2_BUCKET_NAME=your-bucket-name
     R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
     R2_REGION_NAME=auto
     R2_CUSTOM_DOMAIN=your-custom-domain.com  # Optional
     ```
   - Files will automatically be stored in R2 instead of local storage

## Initial Data Setup

After creating the admin user, you'll need to set up:

1. **Create tenants** in the admin interface (linked to Django users)
2. **Set up rent agreements** for each tenant
3. **Configure utility types** (Electricity, Gas, Water, Internet, Condominio)
4. **Configure meter types** with reading periods
5. **Upload utility bills** and mark them as paid/unpaid

## Romanian Localization

- Currency display: RON for utilities, EUR + RON for rent
- Date formats: Adapted for Romanian locale
- Time zone: Europe/Bucharest

## Security Features

- CSRF protection
- Secure password hashing
- File upload restrictions
- Admin interface protection
- HTTPS enforcement in production

## Development

The application uses:
- Django 4.2+
- Bootstrap 5 for UI
- SQLite for development (easily switchable to PostgreSQL)
- Docker for containerization
- WhiteNoise for static file serving in production
