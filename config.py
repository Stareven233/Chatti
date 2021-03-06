from os import getenv
from os.path import dirname, sep


STATICS_DEST = dirname(__file__)+sep+'app'+sep+'static'+sep+'img'+sep
GLOBAL_ERROR_CODE = '400 401 403 404 500'.split()
MSG_PER_PAGE = 20
DEFAULT_AVATAR = 'default.jpeg'
ALLOWED_IMG_EXT = 'jpg jpeg png'.split()


class Config(object):
    SECRET_KEY = 'M<JZ7]6P-r_C0C3hNzY#gbOjY'
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    JSON_AS_ASCII = False
    REDIS_URL = {'host': 'localhost', 'port': 6379, 'db': 1, 'password': getenv('DATABASE_PW')}
    # USE_X_SENDFILE = True
