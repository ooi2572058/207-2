from django.conf import settings
from django.db import models


class UserBook(models.Model):
    """保有書籍テーブル (user_books)

    ユーザーがどの本を所有しているかと、その書籍に対する個人の備考を管理する。
    定義元: テーブル定義書「保有書籍テーブル」
    """

    TYPE_CHOICES = [
        (Falsex, "物理本"),
        (True, "ネット媒体"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE,
        related_name="user_books",
        verbose_name="ユーザー",
    )

    book = models.ForeignKey(
        "books.Book",
        on_delete=models.PROTECT,  
        related_name="user_books",
        verbose_name="書籍",
    )

    memo = models.CharField(
        "メモ",
        max_length=255,
        null=True,
        blank=True,
    )

    type = models.BooleanField(
        "書籍タイプ",
        choices=TYPE_CHOICES,
        default=False,
        help_text="False=物理本、True=ネット媒体",
    )

    class Meta:
        db_table = "user_books"
        verbose_name = "保有書籍"
        verbose_name_plural = "保有書籍"

    def __str__(self):
        return f"{self.user_id}:{self.book_id}"
