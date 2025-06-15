# Windsurf Rules for CINAF Management APP

## Project Overview
This is a Django-based gym management application that runs in Docker containers. The application manages gym members, workouts, payments, attendance tracking, and exercise routines for a gym called CINAF. The application is designed for a Spanish-speaking audience (Argentina) and includes localization settings.

## Development Environment
- The project runs using docker-compose
- Main components:
  - Web service (Django 4.2+ with Python 3.11)
  - Database service (PostgreSQL 15)
- Time zone is set to America/Argentina/Buenos_Aires

## Rules for Development

### General Rules
1. **Ask about anything unclear before starting the task**
2. The project is running in docker-compose
3. Always test changes in the Docker environment before committing
4. Follow Django best practices for code organization and structure
5. The application is in Spanish (Argentina) - maintain consistent language usage
6. The project uses Bootstrap for frontend styling
7. Comments in the code are in Spanish - maintain this convention

### Database Operations
1. Database migrations should be run through Docker:
   ```
   docker-compose run web python manage.py makemigrations
   docker-compose run web python manage.py migrate
   ```
2. Database backups can be created using:
   ```
   docker exec -t gymapp-db-1 pg_dump -U gymuser -F c -b -v -f /tmp/backup_gymdb.backup gymdb
   ```
3. Database restoration:
   ```
   docker cp backup_gymdb.backup gymapp-db-1:/tmp/
   docker exec -it gymapp-db-1 pg_restore -U gymuser -d gymdb --clean --if-exists -v /tmp/backup_gymdb.backup
   ```
4. Legacy data migration is handled through CSV files:
   ```
   docker-compose exec web bash
   python3 legacy_data_migration/scripts/cargar_todo.py
   ```

### Environment Setup
1. Use the .env file for environment variables (based on .env.example)
2. To restart the environment:
   ```
   docker-compose down -v --remove-orphans
   docker-compose up --build
   ```
3. The entrypoint.sh script handles:
   - Waiting for the database to be available
   - Running migrations
   - Creating a superuser if one doesn't exist
   - Collecting static files
   - Starting the development server
4. The application currently runs in development mode (using Django's runserver instead of Gunicorn)

### Code Style
1. Maintain consistent styling across the application
2. Follow the existing patterns for views, models, and templates
3. Standardize table styles and actions throughout the app (in progress)
4. Model methods are well-documented with Spanish comments
5. Views are organized by functionality (ABM - Alta, Baja, Modificación)
6. Use Bootstrap for styling and maintain consistent UI patterns
7. Follow the established pattern for form validation and error messages

### Feature Development
1. Refer to the README.md for the list of pending tasks and their priorities
2. Focus on maintaining a consistent user experience across the application
3. Consider the Spanish-language context of the application when developing features
4. The application is organized into several Django apps:
   - socios: Member management
   - registros: Attendance tracking
   - pagos: Payment management
   - modalidades: Membership types
   - ejercicios: Exercise tracking
5. Follow the established patterns for CRUD operations in each app
6. Maintain consistent error handling and success messages

### Deployment
1. The application is intended to be deployed on GCP Free Tier (future goal)
2. Consider adding Nginx for production (future goal)
3. For production deployment, uncomment the Gunicorn line in entrypoint.sh and comment out the development server line
4. The application includes health checks for the web service
5. Static files are collected during the startup process
6. Database persistence is handled through Docker volumes

### Data Models
1. Key models in the application:
   - Socio: Gym member with personal information and status tracking
   - Observacion: Observations/notes about members
   - RegistroEntrada: Attendance records
   - Pago: Payment records
   - HistorialModalidad: Membership type history
   - Ejercicio: Exercise definitions
   - RegistroEjercicio: Exercise tracking records
2. Model relationships should be maintained according to the existing patterns
3. Use Django's ORM features for queries rather than raw SQL

### Testing
1. Test all changes in the Docker environment before committing
2. Ensure that database migrations work correctly
3. Test both the backend functionality and frontend rendering

### Security
1. Keep the SECRET_KEY in the .env file and never commit it to version control
2. DEBUG mode should be disabled in production
3. Follow Django's security best practices

### Localization
1. The application uses Spanish (Argentina) as the default language
2. Date formats follow the Argentine standard (DD/MM/YYYY)
3. Time zone is set to America/Argentina/Buenos_Aires
