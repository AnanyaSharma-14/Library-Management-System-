from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')
def about(request):
    return HttpResponse("About")
def contact(request):
    return HttpResponse("Contact")
def services(request):
    return HttpResponse("Services")