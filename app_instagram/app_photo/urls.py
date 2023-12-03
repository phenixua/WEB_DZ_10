from django.urls import path, include

from . import views

app_name = "quote"

urlpatterns = [
    path('', views.index, name='home'),  # quote:home
    path('pictures/', views.pictures, name='pictures'),
    path('upload/', views.upload, name='upload'),
    path('pictures/edit/<int:pic_id>', views.edit, name='edit'),
    path('pictures/remove/<int:pic_id>', views.remove, name='remove')
]
