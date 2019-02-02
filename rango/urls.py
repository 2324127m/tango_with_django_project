from django.conf.urls import url
from rango import views

#app_name = 'rango'

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^about/', views.about, name='about'),

	url(r'^add_category/$', views.add_category, name='add_category'),
	url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
	
	# Parameter: category_name_slug. Can be accessed in our view (it takes a parameter)
	# consists of a sequence of alphanumeric character and hyphens which are between the
	# rango/category/id.../
	# Sequence will be stored into parameter and passed to views.show_category()
	# No match => 404 not found
	url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.show_category, name='show_category')

]