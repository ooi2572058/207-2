from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Library(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="libraries",
    )
    company = models.ForeignKey(
        "Company",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="libraries",
        db_column="companies_id",
    )
    book = models.ForeignKey(
        "BookMaster",
        on_delete=models.CASCADE,
        related_name="libraries",
    )
    memo = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    type = models.BooleanField(
        default=False,  # False=物理本, True=ネット媒体
    )
    lend_status = models.BooleanField(
        default=False,  # False=貸出可能, True=貸出不可
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "libraries"
        constraints = [
            # user と company のどちらか一方は必ず NOT NULL である制約
            models.CheckConstraint(
                condition=Q(user__isnull=False) | Q(company__isnull=False),
                name="library_user_or_company_not_null",
            )
        ]

    def clean(self):
        super().clean()
        if not self.user and not self.company:
            raise ValidationError("ユーザーまたは法人のどちらか一方を指定してください。")

    def __str__(self):
        owner = f"User:{self.user_id}" if self.user_id else f"Company:{self.company_id}"
        return f"{owner} - Book:{self.book_id}"
