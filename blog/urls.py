from django.urls import path

from . import views

urlpatterns = (
	path('', views.index),
	path('index.html', views.index),
	path('<int:category>', views.index),
	path('article/<int:article>', views.article),
)
