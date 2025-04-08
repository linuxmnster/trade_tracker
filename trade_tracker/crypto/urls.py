from django.urls import path
from . import views

urlpatterns = [
    path("", views.crypto_home, name="crypto_home"),
    path("form/", views.crypto_form_page, name="crypto_form_page"),  
    path("process_form/", views.crypto_process_form, name="crypto_process_form"),
    path("download_csv/", views.crypto_download_csv, name="crypto_download_csv"),
    path("download_correlation/", views.crypto_download_correlation, name="crypto_download_correlation"),
]