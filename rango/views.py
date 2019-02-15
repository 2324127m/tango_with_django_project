from django.shortcuts import render
# from django.http import HttpResponse, HttpResponseRedirect
# from django.core.urlresolvers import reverse

# from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Import the Category and Page model
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

from datetime import datetime
from rango.webhose_search import run_query


def index(request):
	request.session.set_test_cookie()
	# Retrieve top 5 most viewed pages
	page_list = Page.objects.order_by('-views')[:5]

	# Query the database for a list of ALL categories currently stored
	# Order the categories by no. of likes in descending order 100 99 98 etc.
	# Retrieve the top 5 only - or all if less than 5
	# Place the list in our context_dict dictionary
	# that will be passed to the template engine

	category_list = Category.objects.order_by('-likes')[:5]

	context_dict = {
		'categories': category_list,
		'pages': page_list
	}

	# Call the helper function to handle the cookies
	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']

	# Obtain our response object
	response = render(request, 'rango/index.html', context_dict)

	# Return response back to the user, updating any cookies that need changed
	return response


def about(request):
	if request.session.test_cookie_worked():
		print("TEST COOKIE WORKED")
		request.session.delete_test_cookie()

	visitor_cookie_handler(request)
	context_dict = {
		'visits': request.session['visits']
	}

	return render(request, 'rango/about.html', context_dict)


def show_category(request, category_name_slug):
	# Create a context dictionary which we can pass to the template rendering engine.
	context_dict = {}

	try:
		# Can we find a category name slug with the given name?
		# If we can't, the .get() method raises a DoesNotExist exception
		# So the .get() method returns one model instance or raises an exception
		category = Category.objects.get(slug=category_name_slug)

		# Retrieve all of the associated pages
		# Note that filter() will return a list of pages or an empty list
		pages = Page.objects.filter(category=category)

		# Adds our results list to the template context under name pages
		context_dict["pages"] = pages

		# We also add the category object from the database to the context dictionary
		# We'll use this in the template to verify that the category exists
		context_dict['category'] = category
	except Category.DoesNotExist:
		# We get here if we didn't find the specified category, don't do anything
		# the template will display the "no category" message for us
		context_dict['category'] = None
		context_dict['pages'] = None

	# Go render the response and return it to the client
	return render(request, 'rango/category.html', context_dict)


@login_required()
def add_category(request):
	form = CategoryForm()

	# Was the Http request a post?
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# Have we been provided with a valid form?
		if form.is_valid():
			# Save the new category to the database
			form.save(commit=True)
			# Now that the category is saved
			# We could give a confirmation message
			# But since the most recent category added is on the index page
			# Then we can direct the user back to the index page
			return index(request)
		else:
			# The supplied form contained errors
			# just print them to the terminal
			print(form.errors)

	# Will handle the bad form, new form, or no form supplied cases
	# Render the form with error messages (if any).
	return render(request, 'rango/add_category.html', {'form': form})


@login_required()
def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None

	form = PageForm()

	# Was the Http request a post?
	if request.method == 'POST':
		form = PageForm(request.POST)

		# Have we been provided with a valid form?
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)
		else:
			# The supplied form contained errors
			# just print them to the terminal
			print(form.errors)

	context_dict = {'form': form, "category": category}
	return render(request, 'rango/add_page.html', context_dict)


"""
def register(request):
	# tells template whether the registration was successful
	registered = False

	if request.method == 'POST':
		# attempt to grab info from raw form
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			# Save user form data
			user = user_form.save()

			# hash password with set_password method, once hashed, save it
			user.set_password(user.password)
			user.save()

			# now let's sort out UserProfile instance, need to set user attributes ourselves
			# so set commit=False, it will delay saving the model until we're ready
			# avoids integrity problems

			profile = profile_form.save(commit=False)
			profile.user = user

			# if they provided a pic, get it from input form and put it into UserProfile model
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# save model instance
			profile.save()

			registered = True
		else:
			print(user_form.errors, profile_form.errors)
	else:
		# not a HTTP POST request, render again (Blank)
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request, 'rango/register.html', {
		'user_form': user_form,
		'profile_form': profile_form,
		'registered': registered
	})


def user_login(request):
	if request.method == 'POST':
		# Gather user and pass provided by user, info obtained from login form
		# We use request.POST.get() as it will return none if the value does not
		# exist whereas request.POST[] will raise a KeyError exception
		username = request.POST.get('username')
		password = request.POST.get('password')

		# use django to see if user/pass combo is valid, a User object is returned if so
		user = authenticate(username=username, password=password)

		if user:
			# if account is active (it may have been disabled)
			if user.is_active:
				# valid and active => login then send back to homepage
				login(request, user)
				return HttpResponseRedirect(reverse('index'))
			else:
				return HttpResponse("Your Rango account is disabled.")
		else:
			# bad login details provided
			print("Invalid login details: {0}, {1}".format(username, password))
			return render(request, 'rango/login.html', {
				'invalid_details': True
			})

	else:
		# Request is not HTTP POST so display login form
		# no context variables to pass to template
		return render(request, 'rango/login.html', {})


# Only those who are logged in can log out
@login_required()
def user_logout(request):
	# since we know they are logged in
	logout(request)
	return HttpResponseRedirect(reverse('index'))
"""


@login_required
def restricted(request):
	return render(request, 'rango/restricted.html', {})


# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
	val = request.session.get(cookie)
	if not val:
		val = default_val
	return val


# A Helper method
def visitor_cookie_handler(request):

	visits = int(get_server_side_cookie(request, 'visits', '1'))

	last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))

	# Creates datetime object of the specified format
	last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

	# If it's been more than a day since the last visit
	if (datetime.now() - last_visit_time).days > 1:
		visits = visits + 1
		# Update the last visit cookie now that we have updated the count
		request.session['last_visit'] = str(datetime.now())
	else:
		# Set the last visit cookie
		request.session['last_visit'] = last_visit_cookie

	# Update/set the visits cookie
	request.session['visits'] = visits


def search(request):
	result_list = []
	context_dict = {}

	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			result_list = run_query(query)
			context_dict['user_query'] = query

	context_dict['result_list'] = result_list

	return render(request, 'rango/search.html', context_dict)
