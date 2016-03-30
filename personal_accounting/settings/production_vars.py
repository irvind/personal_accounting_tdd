import envs

STATIC_ROOT_PATH = '../static'      # relative to BASE_DIR
DOMAIN_NAME = 'accounting.irvind.me'

DB_NAME = 'accounting'
DB_USER = 'accounting'
DB_PASSWORD = envs.get_prod_db_password()
DB_HOST = '127.0.0.1'
DB_PORT = 5432
