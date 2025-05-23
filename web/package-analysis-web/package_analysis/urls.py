from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("contact/", views.contact, name="contact"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("get_wolfi_packages/", views.get_wolfi_packages, name="get_wolfi_packages"),
    path("get_maven_packages/", views.get_maven_packages, name="get_maven_packages"),
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
    # get rubygems
    path("get_rubygems_packages/", views.get_rubygems_packages, name="get_rubygems_packages"),
    path("get_rubygems_versions/", views.get_rubygems_versions, name="get_rubygems_versions"),
     
    path("configure/", views.configure, name="configure"),
    path("analyze/", views.analyze, name="analyze"),
    path("results/", views.results, name="results"),
    # upload_sample is submit local sample package. 
    path("upload_sample/", views.upload_sample, name="upload_sample"),
    # submit_sample is submit available existing package. run mutiple tools: typosquatting, and source code finder.
    path("submit_sample/", views.submit_sample, name="submit_sample"),
    # find source code repository of the package.
    path("find_source_code/", views.find_source_code, name="find_source_code"),
    # find typosquatting of the package.
    path("find_typosquatting/", views.find_typosquatting, name="find_typosquatting"),
    # static analysis using bandit4mal tool
    path("bandit4mal/", views.bandit4mal, name="bandit4mal"),
    # dynamic analysis of the package.
    path("dynamic_analysis/", views.dynamic_analysis, name="dynamic_analysis"),
    # malcontentpath("malcontent/", views.malcontent, name="malcontent"),ath("malcontent/", views.malcontent, name="malcontent"),"malcontent/", views.malcontent, name="malcontent",("malcontent/", views.malcontent, name="malcontent"),
    path("malcontent/", views.malcontent, name="malcontent"),
    # LastPyMile
    path("lastpymile/", views.lastpymile, name="lastpymile"),
    path("report/<int:report_id>/", views.report_detail, name="report"),
    path("get_all_report/", views.get_all_report, name="get_report"),
    path("get_report/<int:report_id>/", views.get_report, name="get_report"),
    path("analyzed_samples/", views.analyzed_samples, name="analyzed_samples"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
