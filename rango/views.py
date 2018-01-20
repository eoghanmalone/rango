from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    # construct a dictionary to pass to the template engine as its
    # context
    #NOTE: the key bold message is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
    
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    return HttpResponse("Rango says you are in the about page")
