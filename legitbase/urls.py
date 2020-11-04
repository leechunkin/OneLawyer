from django.urls import path, include
from . import views

urlpatterns = [
	path('', views.index, name='home'),
	path('categories.js', views.categories, name='categories_js'),
	path('service/<int:service>/', views.service, name='service'),
	path('lawyer/<int:lawyer_post_id>/', views.lawyer_post_get, name='lawyer_post'),
	path('lawyer-service/<int:lawyer_service_id>/', views.lawyer_service_get, name='lawyer-service'),
	path('lawyer-service/<int:lawyer_service_id>/request', views.lawyer_service_request, name='lawyer-service-req'),
	path('lawyer-service-request/<uuid:request_id>/validate', views.lawyer_service_request_validate, name='lawyer-service-req-validate'),
	path('lsrv/<str:jwt>', views.lawyer_service_request_validated, name='lawyer-service-req-validated'),
	path('lsr/<str:jwt>', views.lawyer_service_request_view, name='lawyer-service-req-view'),
	path('lsr/ack/<str:jwt>', views.lawyer_service_request_ack, name='lawyer-service-req-ack'),
	path('lsr/abl/<str:jwt>', views.lawyer_service_request_ack_by_lawyer, name='lawyer-service-req-ack-by-lawyer'),
	path('lsr/comment/<str:jwt>', views.lawyer_service_request_endorsement, name='lawyer-service-req-endorsement'),
	path('lawfirm/', include('legitbase.lawfirm.urls')),
]
