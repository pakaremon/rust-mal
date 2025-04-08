from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

from .forms import PackageSubmitForm

from .helper import Helper
import json

from django.core.files.storage import FileSystemStorage

from .models import Package, Report
from collections import Counter




def save_report(reports):
    ''' Save the report to the database '''
    package = Package(package_name=reports['packages']['package_name'], package_version=reports['packages']['package_version'],
                        ecosystem=reports['packages']['ecosystem'])
    package.save()

    syscalls_counter = Counter(reports['install']['syscalls'] + reports['import']['syscalls'])
    the_report = Report(
        package=package,
        time=reports['time'],
        num_files=reports['install']['num_files'] + reports['import']['num_files'],
        num_commands=reports['install']['num_commands'] + reports['import']['num_commands'],
        num_network_connections=reports['install']['num_network_connections'] + reports['import']['num_network_connections'],
        num_system_calls=reports['install']['num_system_calls'] + reports['import']['num_system_calls'],
        files={
            'read': list(set(reports['install']['files']['read'] + reports['import']['files']['read'])),
            'write': list(set(reports['install']['files']['write'] + reports['import']['files']['write'])),
            'delete': list(set(reports['install']['files']['delete'] + reports['import']['files']['delete'])),
        },
        dns=list(set(reports['install']['dns'] + reports['import']['dns'])),
        ips=[dict(t) for t in {tuple(ip.items()) for ip in (reports['install']['ips'] + reports['import']['ips'])}],
        commands=list({tuple(cmd) if isinstance(cmd, list) else cmd for cmd in reports['install']['commands'] + reports['import']['commands']}),
        syscalls=list(syscalls_counter.items()),
    )
    the_report.save()

def dashboard(request):
    form = PackageSubmitForm()
    return render(request, 'package_analysis/dashboard.html', {'form': form})

def submit_sample(request):
    ''' Enter package name, version and ecosystem to analyze the package.
      The package are already in the Wolfi registry'''
    if request.method == 'POST':
        form = PackageSubmitForm(request.POST)
        if form.is_valid():

            package_name = form.cleaned_data['package_name']
            package_version = form.cleaned_data['package_version']
            ecosystem = form.cleaned_data['ecosystem']
            # Process the form data (e.g., save to database, call an API, etc.)
            print(f"Package Name: {package_name}, Package Version: {package_version}, Ecosystem: {ecosystem}")

            reports = Helper.run_package_analysis(package_name,
                                                   package_version, ecosystem)
            save_report(reports)
            latest_report = Report.objects.latest('id')
            reports['id'] = latest_report.id
            return JsonResponse(reports)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def upload_sample(request):
    ''' Upload sample apk file and analysis it'''
    if request.method == 'POST' and request.FILES['file']:
        
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)
        reports = Helper.handle_uploaded_file(uploaded_file_url) 
        # Save to database
        save_report(reports)
        latest_report = Report.objects.latest('id')
        reports['id'] = latest_report.id
        return JsonResponse(reports)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    


def report_detail(request, report_id):
    '''Report detail analysis result of the package'''
    report = Report.objects.get(pk=report_id)
    return render(request, 'package_analysis/report_detail.html', {'report': report})

def get_all_report(request):
    report = Report.objects.all()
    results = {}
    for r in report:
        results[r.id] = {
            'id': r.id,
            'package_name': r.package.package_name,
            'package_version': r.package.package_version,
            'ecosystem': r.package.ecosystem,
            'time': r.time,
        }

    return JsonResponse(results)

def get_report(request, report_id):
    report = Report.objects.get(pk=report_id)
    results = {
        'package_name': report.package.package_name,
        'package_version': report.package.package_version,
        'ecosystem': report.package.ecosystem,
        'time': report.time,
        'num_files': report.num_files,
        'num_commands': report.num_commands,
        'num_network_connections': report.num_network_connections,
        'num_system_calls': report.num_system_calls,
        'files': report.files,
        'dns': report.dns,
        'ips': report.ips,
        'commands': report.commands,
        'syscalls': report.syscalls,
    }
    return JsonResponse(results)

def analyzed_samples(request):
    '''List of analyzed samples, sorted by id'''

    packages = Package.objects.all().order_by('-id')

    return render(request, 'package_analysis/analyzed_samples.html', {'packages': packages})



def get_rust_packages(request):
    return JsonResponse(Helper.get_rust_packages())

def get_pypi_packages(request):
    return JsonResponse(Helper.get_pypi_packages() )

def get_pypi_versions(request):
    package_name = request.GET.get('package_name', None)
    if not package_name:
        return JsonResponse({'error': 'Package name is required'}, status=400)
    
    import requests
    def get_versions(package_name):
        """Get all available versions of a package from PyPI."""
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            versions = list(data['releases'].keys())  # Directly convert to list
            return versions
        else:
            return []  # Return empty list if request fails
         
    # Get the versions of the package
    versions = get_versions(package_name)

    return JsonResponse({"versions":versions})


def configure(request):
    return render(request, "package_analysis/configureSubmit.html")

def analyze(request):
    return render(request, "package_analysis/analyzing.html")

def results(request):
    return render(request, "package_analysis/reports.html")



