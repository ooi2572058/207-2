from django.conf import settings
from django.db import models
from django.db.models import Q


class Product(models.Model):
    """商品テーブル（products）"""

    name = models.CharField(
        max_length=255,
        verbose_name="商品名",
    )
    price = models.IntegerField(
        verbose_name="価格",
    )
    stocks = models.IntegerField(
        verbose_name="在庫",
    )
    image_path = models.CharField(
        max_length=255,
        verbose_name="商品画像パス",
    )
    detail = models.TextField(
        verbose_name="詳細",
    )
    genres = models.CharField(
        max_length=255,
        verbose_name="ジャンル",
    )

    class Meta:
        db_table = "products"
        verbose_name = "商品テーブル"
        verbose_name_plural = "商品テーブル"

    def __str__(self):
        return self.name


class UserProduct(models.Model):
    """出品テーブル（user_products）"""

    user = models.ForeignKey(
        "accounts.users",
        db_column="user_id",
        on_delete=models.CASCADE,
        verbose_name="ユーザーid",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="タイトル",
    )
    isbn = models.CharField(
        max_length=255,
        verbose_name="ISBNコード",
    )
    author = models.CharField(
        max_length=255,
        verbose_name="著者名",
    )
    category = models.CharField(
        max_length=255,
        verbose_name="カテゴリ",
    )
    item_condition = models.CharField(
        max_length=10,
        verbose_name="商品の状態",
    )
    price = models.IntegerField(
        verbose_name="価格",
    )
    overview = models.TextField(
        verbose_name="商品説明",
    )
    image_path = models.TextField(
        verbose_name="商品画像パス",
    )
    created_at = models.DateField(
        auto_now_add=True,
        verbose_name="作成日時",
    )
    updated_at = models.DateField(
        auto_now=True,
        null=True,
        blank=True,
        verbose_name="更新日時",
    )
    deleted_at = models.DateField(
        null=True,
        blank=True,
        verbose_name="削除日時",
    )

    class Meta:
        db_table = "user_products"
        verbose_name = "出品テーブル"
        verbose_name_plural = "出品テーブル"

    def __str__(self):
        return self.title


class Cart(models.Model):
    """カートテーブル（carts）"""

    product = models.ForeignKey(
        Product,
        db_column="product_id",
        on_delete=models.CASCADE,
        verbose_name="商品ID",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="user_id",
        on_delete=models.CASCADE,
        verbose_name="ユーザーID",
    )
    quantity = models.IntegerField(
        verbose_name="数量",
    )

    class Meta:
        db_table = "carts"
        verbose_name = "カートテーブル"
        verbose_name_plural = "カートテーブル"

    def __str__(self):
        return f"カート #{self.pk}"


class Order(models.Model):
    """注文テーブル（orders）"""

    order_number = models.CharField(
        max_length=30,
        verbose_name="注文番号",
        unique=True,
    )
    ordered_at = models.DateTimeField(
        verbose_name="注文日時",
    )
    total_amount = models.PositiveIntegerField(
        verbose_name="合計金額",
    )
    payment_method = models.CharField(
        max_length=255,
        verbose_name="支払方法",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="user_id",
        on_delete=models.SET_NULL,
        verbose_name="ユーザーID",
    )
    user_name = models.CharField(
        max_length=50,
        verbose_name="本名",
    )
    tel_num = models.CharField(
        max_length=20,
        verbose_name="電話番号",
    )
    postal_code = models.CharField(
        max_length=8,
        verbose_name="郵便番号",
    )
    prefectures = models.CharField(
        max_length=4,
        verbose_name="都道府県",
    )
    city = models.CharField(
        max_length=50,
        verbose_name="市区町村",
    )
    address_line = models.CharField(
        max_length=100,
        verbose_name="番地建物名部屋番",
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
        db_table = "orders"
        verbose_name = "注文テーブル"
        verbose_name_plural = "注文テーブル"

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    """注文明細テーブル（order_items）"""

    product = models.ForeignKey(
        Product,
        db_column="product_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="商品ID",
    )
    user_product = models.ForeignKey(
        UserProduct,
        db_column="user_product_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="出品ID",
    )
    quantity = models.IntegerField(
        db_column="quantity_id",
        verbose_name="数量",
    )
    unit_price = models.IntegerField(
        verbose_name="単価",
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
        db_table = "order_items"
        verbose_name = "注文明細テーブル"
        verbose_name_plural = "注文明細テーブル"
        constraints = [
            models.CheckConstraint(
                check=Q(product__isnull=False) | Q(user_product__isnull=False),
                name="order_item_product_or_user_product_not_null",
            )
        ]

    def __str__(self):
        return f"注文明細 #{self.pk}"