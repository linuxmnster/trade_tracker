from django.urls import path
from . import views

urlpatterns = [
    path("", views.stocks_home, name="stocks_home"),
    path("form/", views.form_page, name="stock_form_page"),  
    path("process_form/", views.process_form, name="process_form"),
    path("download_csv/", views.download_csv, name="download_csv"),
    path("download_correlation/", views.download_correlation, name="download_correlation"),
]