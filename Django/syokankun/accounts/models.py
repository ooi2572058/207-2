from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone  # 【追加】timezone.now() に必須


class Company(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='企業ID')
    name = models.CharField(max_length=100, verbose_name='企業名')
    display_name = models.CharField(max_length=100, verbose_name='表示名')
    email = models.EmailField(max_length=254, verbose_name='メールアドレス')
    corporate_code = models.PositiveIntegerField(unique=True, verbose_name='法人コード')
    lending_days = models.IntegerField(default=14, verbose_name='貸出可能日数')
    is_auto_notification = models.BooleanField(default=True, verbose_name='自動通知設定')
    loan_limits = models.IntegerField(default=2, verbose_name='貸出可能冊数')

    class Meta:
        db_table = 'companies'
        verbose_name = '企業'
        verbose_name_plural = '企業'

    def __str__(self):
        return self.name


# email でユーザーやスーパーユーザーを作成するためのマネージャー
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('メールアドレスは必須です')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('last_name', '管理')
        extra_fields.setdefault('first_name', '太郎')
        extra_fields.setdefault('nickname', 'admin')
        extra_fields.setdefault('tel_num', '00000000000')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# 有効（未退会）ユーザーのみを取得するマネージャー
class ActiveUserManager(CustomUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True, is_active=True)


class User(AbstractUser):
    # AbstractUserの不要なデフォルトフィールドを無効化
    username = None

    ROLE_CHOICES = (
        (1, '一般ユーザー'),
        (2, '法人管理者'),
    )
    CORPORATE_ROLE_CHOICES = (
        (1, '一般'),
        (2, '管理者'),
    )

    id = models.AutoField(primary_key=True, verbose_name='ユーザーID')
    nickname = models.CharField(max_length=50, verbose_name='ニックネーム')
    email = models.EmailField(max_length=254, unique=True, verbose_name='メールアドレス')
    tel_num = models.CharField(max_length=20, verbose_name='電話番号')
    
    postal_code = models.CharField(max_length=8, null=True, blank=True, verbose_name='郵便番号')
    prefectures = models.CharField(max_length=4, null=True, blank=True, verbose_name='都道府県')
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name='市区町村')
    address_line = models.CharField(max_length=100, null=True, blank=True, verbose_name='番地建物名部屋番号')
    
    role = models.IntegerField(default=1, choices=ROLE_CHOICES, verbose_name='権限')
    icon_path = models.CharField(max_length=100, null=True, blank=True, verbose_name='アイコンパス')
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日')
    
    corporate = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        db_column='corporate_id',
        null=True,
        blank=True,
        verbose_name='法人ID'
    )
    
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='退会日時')
    corporate_role = models.IntegerField(choices=CORPORATE_ROLE_CHOICES, null=True, blank=True, verbose_name='法人権限')

    # 【修正】有効ユーザーのみをデフォルトにし、全件取得用を別名で定義
    objects = ActiveUserManager()
    all_objects = CustomUserManager()

    # ログイン時に使用するフィールドを email に指定
    USERNAME_FIELD = 'email'
    # createsuperuser 実行時に対話形式で入力を求めるフィールド
    REQUIRED_FIELDS = ['last_name', 'first_name', 'nickname', 'tel_num']

    class Meta:
        db_table = 'users'
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}".strip()
        return full_name if full_name else self.email
    
    def soft_delete(self):
        """論理削除（退会処理）を実行するメソッド"""
        self.deleted_at = timezone.now()
        self.is_active = False
        # 【修正】updated_at も更新対象に含める
        self.save(update_fields=['deleted_at', 'is_active', 'updated_at'])

    def restore(self):
        """退会を取り消してアカウントを復元するメソッド"""
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=['deleted_at', 'is_active', 'updated_at'])
