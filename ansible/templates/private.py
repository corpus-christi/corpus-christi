# DO NOT COMMIT PRODUCTION SETTINGS TO VERSION CONTROL!

PSQL_HOST = '{{ postgres.hostname }}'
PSQL_USER = '{{ postgres.username }}'
PSQL_PASS = '{{ postgres.password }}'

FLASK_SECRET_KEY = 'big secret'
JWT_SECRET_KEY = 'super secret'

EMAIL_USERNAME = 'test@example.com'
EMAIL_PASSWORD = 'password'
