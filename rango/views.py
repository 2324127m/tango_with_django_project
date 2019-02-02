from django.shortcuts import render

from django.http import HttpResponse

# Import the Category and Page model
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm


def index(request):
	# Retrieve top 5 most viewed pages
	page_list = Page.objects.order_by('-views')[:5]

	# Quuery the database for a list of ALL categories currently stored
	# Order the categories by no. of likes in descending order 100 99 98 etc.
	# Retrieve the top 5 only - or all if less than 5
	# Place the list in our context_dict dictionary
	# that will be passed to the template engine

	category_list = Category.objects.order_by('-likes')[:5]

	context_dict = {'categories': category_list,
					'pages': page_list}

	# Render the response and send it back
	return render(request, 'rango/index.html', context=context_dict)

def about(request):
	return render(request, 'rango/about.html', {})

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
			# The supplied form contaied errors
			# just ptint them to the terminal
			print(form.errors)

	# Will handle the bad form, new form, or no form supplied cases
	# Render the form with error messages (if any).
	return render(request, 'rango/add_category.html', {'form':form})


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

	context_dict = {'form':form, "category":category}
	return render(request, 'rango/add_page.html', context_dict)

def register(request):
	# tells template whether the registration was succesful
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

	return render(request, 'rango/register.html',
		{'user_form': user_form,
		'profile_from': profile_form,
		'registered': registered })
