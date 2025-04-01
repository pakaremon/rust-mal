from django import forms

import json
import os

from .helper import Helper


packages = Helper.get_rust_packages()
all_versions = []
for pkg in packages.keys():
    all_versions.extend(packages[pkg])

all_versions = list(set(all_versions))

class PackageSubmitForm(forms.Form):

    package_name = forms.CharField(
        label='Package Name', 
        max_length=100, 
        widget=forms.TextInput(attrs={
            'placeholder': 'Submit package name', 
            'class': 'form-control',   
            'id': 'package_name',
            'list': 'package_name_list'
        })
    )

    

        
    package_version = forms.ChoiceField(
        label='Package Version',
        choices=[('', 'Select a version')] + [(version, version) for version in all_versions],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'package_version',
            'disabled': 'disabled'
        })
    )

    ecosystem = forms.ChoiceField(
        label='Ecosystem',
        choices=[
            ('crates.io', 'Crates.io'),
            ('wolfi', 'Wolfi'),
            ('npm', 'npm'),
            ('pypi', 'PyPI'),
            ('rubygems', 'RubyGems'),
            ('maven_central', 'Maven Central'),
            ('packagist', 'Packagist'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )