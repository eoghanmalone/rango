from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says hey there partner! <a href='/rango/about/'>About page</a>")

def about(request):
    return HttpResponse("Rango says you are in the about page")
