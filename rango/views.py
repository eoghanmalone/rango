from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')

    if(datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        visits = 1
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits

def index(request):
    
    #context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
    request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    print(request.session['visits'])
    response = render(request, 'rango/index.html', context=context_dict)
    return response

def about(request):
    context_dict = {}
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    print(request.session['visits'])

    return render(request, 'rango/about.html', context=context_dict)
    #return HttpResponse("Rango says here is the about page. <a href='/rango/'>View Index Page</a>")

def show_category(request, category_name_slug):
    #Create a context dictionary which we can pass to the
    # template rendering engine
    context_dict = {}

    try:

        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception
        category = Category.objects.get(slug=category_name_slug)

        #Retrieve all of the associated pages.
        # Note that filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary
        # We'll use this in the template to verify that the category existss
        context_dict['category'] = category

    except Category.DoesNotExist:
        #We get here if we didn't find the specified category
        #Don't do anything
        # the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None

    # Go render the response and return it to the client
    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    form = CategoryForm()
    
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        # Have we been provided with a valid form?
        if form.is_valid():

            # Save the new category to the database.
            form.save(commit=True)

            # Now that the category is saved
            # We could give a confirmation message
            # But instead since the most recent catergory added is on the index page
            # Then we can direct the user back to the index page.
            return index(request)

        else:
            # The supplied form contained errors -
        # just print them to the terminal.

            # The supplied form contained errors - just print them to the terminal.
            print(form.errors)

    # Will handle the bad form (or form details), new form or no form supplied cases.
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):

    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':

        form = PageForm(request.POST)
        if form.is_valid():

            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                # probably better to use a redirect here.
            return show_category(request, category_name_slug)

        else:
            print(form.errors)

    context_dict = {'form':form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


# chapter 9 page 113
def register(request):

    registered = False

    if request.method == 'POST':

        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True

        else:
            
            print(user_form.errors, profile_form.errors)
    else:
        
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


#chapter 9 page 118
def user_login(request):

    if request.method == 'POST':
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username,password))
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html', {})


# page 122        
@login_required
def restricted(request):
    #return HttpResponse("Since you're logged in, you can see this text!")
    return render(request, 'rango/restricted.html', {})

# page 124
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
        
        
