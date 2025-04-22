from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

from .forms import PackageSubmitForm

from .helper import Helper
import json

from django.core.files.storage import FileSystemStorage

from .models import Package, Report
from collections import Counter
from concurrent.futures import ThreadPoolExecutor




def save_report(reports):
    ''' Save the report to the database '''
    package, created = Package.objects.get_or_create(
        package_name=reports['packages']['package_name'],
        package_version=reports['packages']['package_version'],
        ecosystem=reports['packages']['ecosystem']
    )
 
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

def contact(request):
    return render(request, 'package_analysis/homepage/contact.html')
 
def homepage(request):
    return render(request, 'package_analysis/homepage/homepage.html')

def dynamic_analysis(request):
    # this tool using package-analysis tools to analyze the package.
    if request.method == 'POST':
        print("dynamic analysis Post ^^^^")
        form = PackageSubmitForm(request.POST)
        if form.is_valid():
            print("dynamic analysis form is valid")
            package_name = form.cleaned_data['package_name']
            package_version = form.cleaned_data['package_version']
            ecosystem = form.cleaned_data['ecosystem']

            # Process the form data (e.g., save to database, call an API, etc.)
            print(f"Package Name: {package_name}, Package Version: {package_version}, Ecosystem: {ecosystem}")
            reports = Helper.run_package_analysis(package_name, package_version, ecosystem)
            return JsonResponse({"dynamic_analysis_report": reports})

    form = PackageSubmitForm()
    return render(request, 'package_analysis/analysis/dynamic_analysis.html', {'form': form}) 



def find_typosquatting(request):
    print("find typosquatting")
    if request.method == 'POST':
        form = PackageSubmitForm(request.POST)
        if form.is_valid():
            package_name = form.cleaned_data['package_name']
            package_version = form.cleaned_data['package_version']
            ecosystem = form.cleaned_data['ecosystem']

            # Process the form data (e.g., save to database, call an API, etc.)
            print(f"find oss-squat:package Name: {package_name}, Package Version: {package_version}, Ecosystem: {ecosystem}")
            typo_candidates = Helper.run_oss_squats(package_name, package_version, ecosystem)
            print("Typo candidates: ", typo_candidates)
            return JsonResponse({'typosquatting_candidates': typo_candidates})
        
    form = PackageSubmitForm()
    return render(request, 'package_analysis/analysis/typosquatting.html', {'form': form})

def find_source_code(request):
    if request.method == 'POST':
        print("find source code")
        form = PackageSubmitForm(request.POST)
        if form.is_valid():
            print("find source code form is valid")
            package_name = form.cleaned_data['package_name']
            package_version = form.cleaned_data['package_version']
            ecosystem = form.cleaned_data['ecosystem']

            # Process the form data (e.g., save to database, call an API, etc.)
            print(f"Package Name: {package_name}, Package Version: {package_version}, Ecosystem: {ecosystem}")
            sources = Helper.run_oss_find_source(package_name, package_version, ecosystem)

            return JsonResponse({'source_urls': sources})
        
    form = PackageSubmitForm()
    return render(request, 'package_analysis/analysis/findsource.html', {'form': form})

def submit_sample(request):
    # TODO: if package has already been analyzed, return the report instead of re-analyzing it.

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

            with ThreadPoolExecutor() as executor:
                future_reports = executor.submit(Helper.run_package_analysis, package_name, package_version, ecosystem)
                future_typosquatting_candidates = executor.submit(Helper.run_oss_squats, package_name, package_version, ecosystem)
                future_sources = executor.submit(Helper.run_oss_find_source, package_name, package_version, ecosystem)

                reports = future_reports.result()
                typo_candidates = future_typosquatting_candidates.result()
                sources = future_sources.result()

                reports['sources'] = sources
                reports['typo_candidates'] = typo_candidates

                print("Typo candidates: ", reports['typo_candidates'])

            
            save_report(reports)
            latest_report = Report.objects.latest('id')
            reports['id'] = latest_report.id
            return JsonResponse(reports)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def upload_sample(request):
    ''' Upload sample  analysis it'''
    if request.method == 'POST' and request.FILES['file']:
         
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)
        ecosystem = request.POST.get('ecosystem', None)
        package_name = request.POST.get('package_name', None)
        package_version = request.POST.get('package_version', None)
        
        reports = Helper.handle_uploaded_file(uploaded_file_url, package_name, package_version, ecosystem)
        
        # Save to database
        # save_report(reports)
        # latest_report = Report.objects.latest('id')
        # reports['id'] = latest_report.id
        return JsonResponse({"dynamic_analysis_report": reports})
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

def get_npm_packages(request):
    return JsonResponse(Helper.get_npm_packages())

@staticmethod
def get_packagist_packages(request):
    return JsonResponse(Helper.get_packagist_packages())

@staticmethod
def get_rubygems_packages(request):
    return JsonResponse(Helper.get_rubygems_packages())

@staticmethod
def get_rubygems_versions(request):
    import requests
    def get_package_versions(package_name):
        url = f"https://rubygems.org/api/v1/versions/{package_name}.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results = []
            for version in data:
                results.append(version['number'])
            return results
        else:
            return []
        
    package_name = request.GET.get('package_name', None)
    if not package_name:
        return JsonResponse({'error': 'Package name is required'}, status=400)
    
    get_package_versions = get_package_versions(package_name)
    return JsonResponse({"versions": get_package_versions})

@staticmethod
def get_packagist_versions(request):
    import requests
    def get_package_versions(package_name):
        url = f"https://repo.packagist.org/p2/{package_name}.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results = []
            for version in data['packages'].get(package_name, []):
                results.append(version['version'])
            return results
        else:
            return []  # Return an empty list if the request fails
    
    package_name = request.GET.get('package_name', None)
    if not package_name:
        return JsonResponse({'error': 'Package name is required'}, status=400)
    
    package_versions = get_package_versions(package_name)
    return JsonResponse({"versions": package_versions})



       
           



def get_npm_versions(request):
    import requests
    def get_package_versions(package_name):
        url = f'https://registry.npmjs.org/{package_name}'
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            versions = list(data.get('versions', {}).keys())
            latest_version = data.get('dist-tags', {}).get('latest')
            
            return versions
        else:
            print(f"Failed to fetch {package_name}: {response.status_code}")
            return None
        
    package_name = request.GET.get('package_name', None)
    if not package_name:
        return JsonResponse({'error': 'Package name is required'}, status=400)
    
    package_versions = get_package_versions(package_name)
    return JsonResponse({"versions": package_versions})

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



