from django.conf import settings
from django.db import models


class Review(models.Model):
    """評価テーブル"""

    book_type = models.CharField(
        max_length=20,
        verbose_name="書籍評価",
    )
    transaction_type = models.CharField(
        max_length=20,
        verbose_name="取引評価",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="reviewer_id",
        on_delete=models.CASCADE,
        related_name="given_reviews",
        verbose_name="レビュー者ID",
    )
    
    reviewee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="reviewee_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_reviews",
        verbose_name="被レビュー者・被評価者ID",
    )
    book = models.ForeignKey(
        "BooksMaster",
        db_column="book_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="書籍ID",
    )
    order = models.ForeignKey(
        "Order",
        db_column="order_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="注文ID",
    )
    rating = models.IntegerField(
        verbose_name="評価",
    )
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name="感想・コメント",
    )
    created_at = models.DateField(
        auto_now_add=True,
        verbose_name="作成日",
    )
    updated_at = models.DateField(
        auto_now=True,
        null=True,
        blank=True,
        verbose_name="更新日",
    )

    class Meta:
        db_table = "reviews"
        verbose_name = "評価テーブル"
        verbose_name_plural = "評価テーブル"

    def __str__(self):
        return f"評価 #{self.pk} ({self.rating})"


class Message(models.Model):
    """メッセージテーブル"""

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="sender_id",
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="送信者ID",
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="receiver_id",
        on_delete=models.CASCADE,
        related_name="received_messages",
        verbose_name="受信者ID",
    )
    body = models.TextField(
        verbose_name="本文",
    )
    sent_at = models.DateTimeField(
        verbose_name="送信日時",
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="既読フラグ",
    )
    created_at = models.DateField(
        auto_now_add=True,
        verbose_name="作成日",
    )
    updated_at = models.DateField(
        auto_now=True,
        null=True,
        blank=True,
        verbose_name="更新日",
    )

    class Meta:
        db_table = "messages"
        verbose_name = "メッセージテーブル"
        verbose_name_plural = "メッセージテーブル"

    def __str__(self):
        return f"メッセージ #{self.pk}"


class Report(models.Model):
    """通報テーブル"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name="通報者ユーザーID",
    )
    target_type = models.IntegerField(
        verbose_name="通報対象種別",
    )
    target_id = models.IntegerField(
        verbose_name="対象ID",
    )
    reason_type = models.IntegerField(
        verbose_name="通報理由区分",
    )
    detail = models.TextField(
        null=True,
        blank=True,
        verbose_name="通報詳細",
    )
    status = models.IntegerField(
        default=0,
        verbose_name="対応ステータス",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時",
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="admin_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="handled_reports",
        verbose_name="対応者",
    )

    class Meta:
        db_table = "reports"
        verbose_name = "通報テーブル"
        verbose_name_plural = "通報テーブル"

    def __str__(self):
        return f"通報 #{self.pk}"


class Inquiry(models.Model):
    """お問い合わせテーブル（inquiries）"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="user_id",
        on_delete=models.CASCADE,
        verbose_name="ユーザーID",
    )
    sender_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="送信者名",
    )
    email = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="返信先メールアドレス",
    )
    category = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="お問い合わせ種別",
    )
    content = models.TextField(
        null=True,
        blank=True,
        verbose_name="お問い合わせ詳細",
    )
    status = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="対応ステータス",
    )
    reply_content = models.TextField(
        null=True,
        blank=True,
        verbose_name="管理者返信内容",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        verbose_name="作成日時",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
        verbose_name="更新日時",
    )

    class Meta:
        db_table = "inquiries"
        verbose_name = "お問い合わせテーブル"
        verbose_name_plural = "お問い合わせテーブル"

    def __str__(self):
        return f"お問い合わせ #{self.pk}"


class PurchaseRequest(models.Model):
    """購入リクエストテーブル（purchase_requests）"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="user_id",
        on_delete=models.CASCADE,
        verbose_name="リクエストユーザーID",
    )
    title = models.CharField(
        max_length=100,
        verbose_name="書籍タイトル",
    )
    author = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="著者名",
    )
    isbn = models.CharField(
        max_length=13,
        null=True,
        blank=True,
        verbose_name="ISBNコード",
    )
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name="リクエスト理由・コメント",
    )
    status = models.IntegerField(
        default=0,
        verbose_name="対応ステータス",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時",
    )
    company = models.ForeignKey(
        "Company",
        db_column="companies_id",
        on_delete=models.CASCADE,
        verbose_name="リクエスト先法人",
    )

    class Meta:
        db_table = "purchase_requests"
        verbose_name = "購入リクエストテーブル"
        verbose_name_plural = "購入リクエストテーブル"

    def __str__(self):
        return self.title