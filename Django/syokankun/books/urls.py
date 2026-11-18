from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('index/0/', views.IndexGuestView.as_view(), name='index_0'),       # 未ログイン (Guest)
    path('index/1/', views.IndexUserView.as_view(), name='index_1'),        # 一般ユーザー (User)
    path('index/2/', views.IndexCorporateView.as_view(), name='index_2'),   # 法人 (Corporate)
    path('index/3/', views.IndexAdminView.as_view(), name='index_3'),       # アドミン (Admin)
]