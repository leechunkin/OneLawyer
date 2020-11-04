"""legit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
import content.views

urlpatterns = [
	path('i18n/', include('django.conf.urls.i18n')),
	path('summernote/', include('django_summernote.urls')),
	path('account/', include('allauth.urls')),
	path('blog/', include('blog.urls')),
	path('', include('legitbase.urls')),
]

urlpatterns += i18n_patterns(
	path('admin/doc/', include('django.contrib.admindocs.urls')),
	path('admin/', admin.site.urls),
	path('account/', include('allauth.urls')),
	path('blog/', include('blog.urls')),
	path('', include('legitbase.urls')),

	# fallback
	path('<path:url>', content.views.basicpage, name='basiccontent'),
)

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)