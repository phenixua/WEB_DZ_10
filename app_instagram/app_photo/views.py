from django.shortcuts import render, render


# Create your views here.

def index(request):
    return render(request, template_name='app_photo/index.html', context={"msg": "Hello world!"})


def pictures(request):
    return render(request, template_name='app_photo/pictures.html', context={})


def upload(request):
    return render(request, template_name='app_photo/upload.html', context={})
