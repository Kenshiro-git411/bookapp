from pathlib import Path
from datetime import timedelta
from decouple import config
from dj_database_url import parse as dburl

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG')

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', # APIフレームワーク
    'api.apps.ApiConfig', # APIアプリ
    'corsheaders', # CORS対応
    'djoser', # ユーザー認証用
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', #corsheaderを使用するために追加
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# next.jsのローカルサーバからアクセスを可能にするurl
CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
]

# JSON Web Token（JWT）認証を実装するためのライブラリ
# セキュアなユーザー認証を行う
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',), #リクエスト認証ヘッダーで使用されるトークンタイプを示す。
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), #アクセストークンの有効期限を示し、アクセストークンが発行されてから60分後に無効になることを示す。
}

REST_FRAMEWORK = {
    #apiエンドポイント（url先）へのアクセスに対するデフォルトの権限クラスを指定する。
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', #全てのエンドポイントに対してユーザーが認証されている必要があることを示す。認証されていないユーザーはエンドポイントにアクセスできないことになっている。
    ],
    #デフォルトの認証クラスを指定する。
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication', #JWTトークンを用いた認証方式を使用することになる。
    ],
}

ROOT_URLCONF = 'djangobook.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangobook.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if DEBUG:
    DATABASES = {
        # localの場合はsqlite3を使用するように設定
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {"default": dburl.config('DATABASE_URL')}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_URL = 'media/'

# LOGOUT_REDIRECT_URL = 'api:top'