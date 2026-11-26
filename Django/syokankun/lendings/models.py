from django.db import models
from books.models import BooksMaster
from accounts.models import User
from django.conf import settings

# Create your models here.
# ステータスの選択肢
class Booleanstatus(models.IntegerChoices):
    PENDING = 0,"処理待ち"
    SHIPPED = 1,"承認済み"
    CANCELED = 2,"却下"

class LendingsModel(models.Model):
    book = models.ForeignKey(
        BooksMaster,verbose_name="書籍ID",db_column="book_id",on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODELS,verbose_name="ユーザーID",
        db_column="user_id,",on_delete=models.CASCADE)
    type = models.BooleanField(
        verbose_name="貸出タイプ",
        default=False)
    @property
    def status_label(self):
        return "返却" if self.type else "貸出"
    status = models.IntegerField(
        choices=Booleanstatus.choices,
        default=Booleanstatus.PENDING,
        verbose_name="ステータス"
    )
    reason = models.CharField(verbose_name="却下理由",max_length=255,null=True,blank=True)
    created_at = models.DateTimeField(verbose_name="作成日時",auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時",auto_now_add=True,null=True)
    

class user_book(models.Model):
    user = models.ForeignKey(
            settings.AUTH_USER_MODELS,verbose_name="ユーザーID",
            db_column="user_id,",on_delete=models.CASCADE)
    book = models.ForeignKey(
            BooksMaster,verbose_name="書籍ID",db_column="book_id",on_delete=models.CASCADE)
    memo = models.CharField(verbose_name="メモ",null=True,blank=True)
    type = models.BooleanField(verbose_name="書籍タイプ",default=False)
    @property
    def type_label(self):
        return "ネット媒体" if self.type else "物理本"
    lend_status = models.BooleanField(verbose_name="貸出ステータス",null=True,blank=True)
    @property
    def status_label(self):
        return "貸出不可" if self.lend_status else "貸出可能"