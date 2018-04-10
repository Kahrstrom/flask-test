
import os
basedir = os.path.abspath(os.path.dirname(__file__))

db_name = os.environ.get('SKILLOCATE_DB', 'skillocate_dev')
db_uid = os.environ.get('SKILLOCATE_UID', 'dev_user')
db_pw = os.environ.get('SKILLOCATE_PW', 'abcde12345')
db_server = os.environ.get('SKILLOCATE_SERVER', 'localhost')
db_port = os.environ.get('SKILLOCATE_PORT', '5432')
host_ip = os.environ.get('SKILLOCATE_HOST', 'localhost')
port = os.environ.get('SKILLOCATE_PORT', 5000)
api_version = 'v1'

admin_email = os.environ.get('SKILLOCATE_ADMIN_EMAIL', 'admin@skillocate.com')
admin_password = os.environ.get('SKILLOCATE_ADMIN_PASSWORD', 'test')

postgres_local_base = "postgresql://{uid}:{pw}@{server}:{port}/".format(
    server=db_server, uid=db_uid, pw=db_pw, port=db_port)


class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'very_secret')
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APPLICATION_ROOT = '/api/{}'.format(api_version)
    APPLICATION_ADMIN_ROOT = '/api/admin/{}'.format(api_version)


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_local_base + db_name


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_local_base + db_name + '_test'
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql:///example'
