from django.urls import path
from .views import fileuploadview

urlpatterns = [
    path('upload/', fileuploadview.as_view(), name='file-upload'),
]

from django.urls import path
from .views import fileuploadview, pdfreportview # <--- import new view

urlpatterns = [
    path('upload/', fileuploadview.as_view(), name='file-upload'),
    path('report/', pdfreportview.as_view(), name='pdf-report'), # <--- add this line
]