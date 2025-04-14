from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path("", views.dashboard, name="dashboard"),
    path("get_rust_packages/", views.get_rust_packages, name="get_rust_packages"),
    path("get_pypi_packages/", views.get_pypi_packages, name="get_pypi_packages"),
    # get_pypi_versions is used to get the available versions of the package in pypi.
    path("get_pypi_versions/", views.get_pypi_versions, name="get_pypi_versions"),
    # get npm
    path("get_npm_packages/", views.get_npm_packages, name="get_npm_packages"),
    path("get_npm_versions/", views.get_npm_versions, name="get_npm_versions"),
    # get packagist
    path("get_packagist_packages/", views.get_packagist_packages, name="get_packagist_packages"),
    path("get_packagist_versions/", views.get_packagist_versions, name="get_packagist_versions"),
     
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
