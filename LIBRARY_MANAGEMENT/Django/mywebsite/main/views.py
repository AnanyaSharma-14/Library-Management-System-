from django.shortcuts import render

def app(request):
    return render(request, 'newApp/app.html')

# Create your views here.
