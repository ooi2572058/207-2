from django.urls import path
from . import views

app_name = 'listing'

urlpatterns = [
    path('', views.listing_list, name='list'),
]