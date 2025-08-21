from django.urls import path
from . import views

urlpatterns = [
    path('', views.news, name='news'),  # Home view for the news app   
]