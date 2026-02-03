from django.urls import path
from .views import AccountListView, CSVUploadView

urlpatterns = [
    path('', AccountListView.as_view(), name='account-list'),
    path('upload/', CSVUploadView.as_view(), name='csv-upload'),
]
