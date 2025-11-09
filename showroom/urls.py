from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('models/', views.models_list, name='models'),
    path('models/<slug:slug>/', views.model_detail, name='model_detail'),
    path('offers/', views.offers, name='offers'),
    path('book-test-ride/', views.book_test_ride, name='book_test_ride'),
    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),
    path('service/', views.service, name='service'),
    path('api/bikes.json', views.bikes_json, name='bikes_json'),
    path('forms/test-ride/', views.submit_test_ride, name='test_ride_submit'),
    path('forms/contact/', views.submit_contact, name='contact_submit'),
    path('forms/service/', views.submit_service, name='service_submit'),
]
