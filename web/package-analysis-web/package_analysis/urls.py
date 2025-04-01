from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path("", views.dashboard, name="dashboard"),
    path("get_rust_packages/", views.get_rust_packages, name="get_rust_packages"),
    path("configure/", views.configure, name="configure"),
    path("analyze/", views.analyze, name="analyze"),
    path("results/", views.results, name="results"),
# upload_sample is submit local sample package. 
    path("upload_sample/", views.upload_sample, name="upload_sample"),
# submit_sample is submit available existing package in crates.io
    path("submit_sample/", views.submit_sample, name="submit_sample"),
    path("report/<int:report_id>/", views.report_detail, name="report"),
    path("get_all_report/", views.get_all_report, name="get_report"),
    path("get_report/<int:report_id>/", views.get_report, name="get_report"),
    path("analyzed_samples/", views.analyzed_samples, name="analyzed_samples"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
