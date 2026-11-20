from django.conf import settings
from django.db import models


class Series(models.Model):
    """シリーズテーブル（series）"""

    series_name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="シリーズ名",
    )
    author = models.CharField(
        max_length=255,
        verbose_name="著者",
    )
    publisher = models.CharField(
        max_length=255,
        verbose_name="出版社",
    )
    total_books_count = models.IntegerField(
        verbose_name="全巻数",
    )

    class Meta:
        db_table = "series"
        verbose_name = "シリーズテーブル"
        verbose_name_plural = "シリーズテーブル"

    def __str__(self):
        return self.series_name


class BooksMaster(models.Model):
    """書籍マスタ（books_master）"""

    isbn = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="ISBNコード",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="タイトル",
    )
    author = models.TextField(
        verbose_name="著者",
    )
    publisher = models.CharField(
        max_length=255,
        verbose_name="出版社",
    )
    synopsis = models.CharField(
        max_length=255,
        verbose_name="あらすじ",
    )
    image_url = models.CharField(
        max_length=500,
        verbose_name="参考画像url",
        null=True,
        blank=True
    )
    sales_date = models.DateField(
        verbose_name="発売日",
        null=True,
        blank=True
    )
    # series.id を参照する外部キー（DBカラム名は series_id、複数巻を許容するため一意制約なし）
    series = models.ForeignKey(
        Series,
        db_column="series_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="シリーズID",
    )
    volume_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="巻数",
    )

    class Meta:
        db_table = "books_master"
        verbose_name = "書籍マスタ"
        verbose_name_plural = "書籍マスタ"

    def __str__(self):
        return self.title


class NotificationSetting(models.Model):
    """通知登録"""

    class Timing(models.IntegerChoices):
        ON_RELEASE = 0, "発売日当日"
        ONE_DAY_BEFORE = 1, "1日前"
        THREE_DAYS_BEFORE = 3, "3日前"
        ONE_WEEK_BEFORE = 7, "1週間前"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="user_id",
        on_delete=models.CASCADE,
        verbose_name="ユーザーID",
    )
    book = models.ForeignKey(
        BooksMaster,
        db_column="book_id",
        on_delete=models.CASCADE,
        verbose_name="書籍ID",
    )
    notify_timing = models.IntegerField(
        choices=Timing.choices,
        default=Timing.ON_RELEASE,
        verbose_name="通知タイミング",
    )
    notify_email = models.BooleanField(
        default=False,
        verbose_name="メール通知",
    )
    notify_push = models.BooleanField(
        default=False,
        verbose_name="ブラウザプッシュ通知",
    )
    memo = models.TextField(
        null=True,
        blank=True,
        verbose_name="メモ・備考",
    )
    is_notified = models.BooleanField(
        default=False,
        verbose_name="通知済みフラグ",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時",
    )

    class Meta:
        db_table = "notification_settings"
        verbose_name = "通知登録"
        verbose_name_plural = "通知登録"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                name="unique_user_book_notification",
            )
        ]

    def __str__(self):
        return f"通知設定 #{self.pk}"