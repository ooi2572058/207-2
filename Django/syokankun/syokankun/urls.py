"""syokankun URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # # 認証・アカウント
    # path('accounts/', include('accounts.urls')),
    
    # # 書籍・検索・カレンダー
    # path('books/', include('books.urls')),
    
    # # ライブラリ
    # path('library/', include('library.urls')),
    
    # # 貸出・返却
    # path('lendings/', include('lendings.urls')),
    
    # # EC・販売・出品
    # path('shop/', include('shop.urls')),
    
    # # コミュニティ・評価・問い合わせ
    # path('community/', include('community.urls')),
    
    # トップページ
    path('', include('books.urls')),
]