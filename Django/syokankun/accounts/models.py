from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ユーザーテーブル (user)"""

    class Role(models.IntegerChoices):
        GENERAL = 1, "一般ユーザー"
        CORPORATE = 2, "法人管理"
        ADMIN = 9, "管理者"

    class CorporateRole(models.IntegerChoices):
        MEMBER = 1, "一般"
        ADMIN = 2, "管理者"

    name = models.CharField("本名", max_length=50)
    nickname = models.CharField("ニックネーム", max_length=50)
    email = models.EmailField("メールアドレス", max_length=255, unique=True)
    tel_num = models.CharField("電話番号", max_length=20)
    postal_code = models.CharField("郵便番号", max_length=8, blank=True, null=True)
    prefectures = models.CharField("都道府県", max_length=10, blank=True, null=True)
    city = models.CharField("市区町村", max_length=50, blank=True, null=True)
    address_line = models.CharField("番地建物名部屋番", max_length=100, blank=True, null=True)
    role = models.IntegerField("権限", choices=Role.choices, default=Role.GENERAL)
    icon_path = models.CharField("アイコンパス", max_length=255, blank=True, null=True)
    corporate = models.ForeignKey(
        "Company",
        on_delete=models.SET_NULL,
        related_name="members",
        verbose_name="法人ID",
        blank=True,
        null=True,
    )
    corporate_role = models.IntegerField(
        "法人権限",
        choices=CorporateRole.choices,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)
    deleted_at = models.DateTimeField("退会日時", blank=True, null=True)

    class Meta:
        db_table = "users"
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"

    @property
    def is_corporate_admin(self) -> bool:
        """法人内の管理者かどうか"""
        return self.corporate_id is not None and self.corporate_role == self.CorporateRole.ADMIN

    @property
    def is_corporate_member(self) -> bool:
        """法人内の一般メンバーかどうか"""
        return self.corporate_id is not None and self.corporate_role == self.CorporateRole.MEMBER

    def __str__(self):
        return f"{self.nickname} ({self.name})"