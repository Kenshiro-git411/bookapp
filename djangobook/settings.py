import os
from pathlib import Path
from datetime import timedelta
from decouple import config
from dj_database_url import parse as dburl

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# 下のローカル用設定箇所のコードに移動
# SECRET_KEY = config('SECRET_KEY')

# DEBUGについては.envファイルに書いてあるため、configファイル(.envファイル)を指定するように書いておく。
DEBUG = config('DEBUG') #デプロイ設定



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
# CORS_ORIGIN_WHITELIST = [
#     "http://localhost:3000",
# ]

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

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = (
    os.path.normpath(os.path.join(BASE_DIR, "assets")),
)
MEDIA_URL = 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# デプロイのため削除
# MEDIA_ROOT = BASE_DIR / 'media'

# ログアウト後のリダイレクト先
# LOGOUT_REDIRECT_URL = 'api:top'

# ログイン後のリダイレクト先
LOGIN_REDIRECT_URL = 'api:top'

# CSRFトークンをチェックする際、指定されたものは信頼あるリクエストとして扱う
CSRF_TRUSTED_ORIGINS = [ "http://127.0.0.1:8000" ]

# メール送信のバックエンドを指定
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# カスタムユーザーモデルをデフォルトに設定
AUTH_USER_MODEL = 'api.User'

try:
    from .local_settings import *
except ImportError:
    pass

# ローカル用設定
if DEBUG:
    import environ

    env = environ.Env()
    env.read_env(os.path.join(BASE_DIR, '.env'))  # .envファイルの読み込み
    SECRET_KEY = env('SECRET_KEY')
    ALLOWED_HOSTS = ['*'] #開発環境ではすべてのホストからのアクセスを許可する。
    # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # メールの内容をコンソールに表示する。
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media') #djangoappプロジェクトフォルダ配下のmediaフォルダを指定。
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = "smtp.gmail.com" # GmailのSMTPサーバー
    EMAIL_PORT = 587 # Gmailサーバーのポート番号
    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
    EMAIL_USE_TLS = True # SMTPサーバーと通信する際に、TLS（セキュア）接続する

# 本番環境用設定
if not DEBUG:
    import environ
    env = environ.Env()
    env.read_env(os.path.join(BASE_DIR, '.env')) #.envファイルの読み込み

    SECRET_KEY = env('SECRET_KEY') #.envファイルからsecretkeyを取得。
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

    # 以下に本番環境のSTATIC_ROOTとMEDIA_ROOTを書く。
    STATIC_ROOT = '/usr/share/nginx/html/static'
    MEDIA_ROOT = '/usr/share/nginx/html/media'

    # メールに関する情報
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = "smtp.gmail.com" # GmailのSMTPサーバー
    EMAIL_PORT = 587 # Gmailサーバーのポート番号
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    EMAIL_USE_TLS = True # SMTPサーバーと通信する際に、TLS（セキュア）接続する

# メール送信における情報
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = "smtp.gmail.com" # GmailのSMTPサーバー
# EMAIL_PORT = 587 # Gmailサーバーのポート番号
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# EMAIL_USE_TLS = True # SMTPサーバーと通信する際に、TLS（セキュア）接続する