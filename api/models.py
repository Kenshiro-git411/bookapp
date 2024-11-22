from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
# from django.contrib.auth.models import User

class CustomUserManager(UserManager):
    # カスタムユーザーマネージャー
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        # 共通のユーザー作成処理
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        # 通常ユーザー作成
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        # スーパーユーザー作成
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


# カスタムユーザーモデル
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def email_user(self, subject, message, from_email=None, **kwargs):
        # ユーザーにメールを送信
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email


# 図書種別テーブル
class Type(models.Model):
    type = models.CharField(max_length=5)

# 著者テーブル
class Author(models.Model):
    author = models.CharField(max_length=20)

# 出版社テーブル
class Publisher(models.Model):
    publisher = models.CharField(max_length=20)

# 雑誌テーブル
class Magazine(models.Model):
    magazine_title = models.CharField(max_length=20, blank=True)

# お気に入りテーブル
class Book(models.Model):
    type = models.ManyToManyField(Type, blank=True) #図書種別
    title = models.CharField(max_length=255) #資料タイトル
    author = models.ManyToManyField(Author, blank=True) #著者
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT) #出版社
    date = models.CharField(max_length=10) #出版年
    magazine_title = models.ManyToManyField(Magazine, blank=True) #掲載誌タイトル
    magazine_number = models.CharField(max_length=20, blank=True) #掲載誌関数
    magazine_date = models.CharField(max_length=10, blank=True) #掲載誌出版年
    page = models.CharField(max_length=20, blank=True) #論文掲載ページ数
    link = models.URLField(blank=True) #図書資料へのアクセスURL
    # email = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', null=True) #username

