import os
# import platform


def is_production():
    if 'production' in os.environ['DJANGO_SETTINGS_MODULE']:
        return True
    return False


def get_environment_settings_module():
    # prod_host_file = None
    # try:
    #     prod_host_file_path = os.path.join(
    #         os.path.dirname(os.path.abspath(__file__)),
    #         'prod_host'
    #     )
    #     prod_host_file = open(prod_host_file_path, 'r')
    #     prod_host_name = prod_host_file.read().strip()

    #     if prod_host_name == platform.node():
    #         return 'personal_accounting.settings.production'
    #     return 'personal_accounting.settings.development'
    # except FileNotFoundError:
    #     return 'personal_accounting.settings.development'
    # finally:
    #     if prod_host_file is not None:
    #         prod_host_file.close()

    if 'ACCOUNTING_PRODUCTION_ENV' in os.environ:
        return 'personal_accounting.settings.production'
    return 'personal_accounting.settings.development'


def get_secret_key():
    if not is_production():
        return 'it_doesnt_really_matter_what_key_is'

    try:
        return os.environ['ACCOUNTING_SECRET_KEY']
    except KeyError:
        raise Exception('Secret key environment variable is not set!')

    # try:
    #     f = open('/etc/djangosecret')
    # except FileNotFoundError:
    #     raise Exception('Secret key file at "/etc/djangosecret" not found!')

    # secret = f.read().strip()
    # f.close()

    # return secret


def get_prod_db_password():
    try:
        return os.environ['ACCOUNTING_DB_PASSWORD']
    except KeyError:
        raise Exception('Database password environment variable is not set!')
