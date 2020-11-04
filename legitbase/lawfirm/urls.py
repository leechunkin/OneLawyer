from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='lawfirm'),
	path('login', views.login),
	path('logout', views.logout),
	path('update', views.update),
	path('lawyer/update', views.lawyer_update),
]
