from django.urls import re_path
from . import views


urlpatterns = [

	re_path(r'^$', views.displayHomePage, name='home-page'),
	re_path(r'home/', views.displayHomePage, name='home-page'),
	re_path(r'professional/', views.displayProfessionalPage, name='professional-page'),
	re_path(r'academic/', views.displayAcademicPage, name='academic-page'),
	re_path(r'music/', views.displayMusicPage, name='music-page'),
	re_path(r'contact/', views.displayContactPage, name='contact-page'),
	re_path(r'.*/', views.handlerView404, name='404-page'),
]

