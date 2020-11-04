from django.urls import path
from . import views

urlpatterns = [
    path('<path:url>', views.basicpage, name='content.basicpage'),
]
