from django.urls import path, include, re_path, reverse
from studies.views import StudyCreateView, StudyDeleteView, StudyUpdateView, StudyDetailView, StudyListView
from .views import TaxonAutocomplete
from . import views
from .decorator import check_if_user_is_author

urlpatterns = [
    path("", StudyListView.as_view(), name="study-list"),
    path("add/", StudyCreateView.as_view(), name="study-add"),
    path("<int:pk>/edit/", check_if_user_is_author(StudyUpdateView.as_view()), name="study-update"),
    path("<int:pk>/delete/", check_if_user_is_author(StudyDeleteView.as_view()), name="study-delete"),
    path('<int:pk>/', check_if_user_is_author(StudyDetailView.as_view()), name='study-detail'),
    re_path(r'^taxon-autocomplete/$',
        TaxonAutocomplete.as_view(),
        name='taxon-autocomplete',),
    path('<int:pk>/export-to-csv', views.export_to_csv, name="export-to-csv"),
    path('<int:pk>/download-analysis', views.download_analysis, name="download-analysis")
]