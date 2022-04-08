from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from requests.api import get, post
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealersby_state
from .models import CarMake, CarModel, CarDealer, DealerReview
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)

def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

def about(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html', context)

def contact_us(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html', context)

# # Update the `get_dealerships` view to render the index page with a list of dealerships
# def get_dealerships(request):
#     context = {}
#     if request.method == "GET":
#         context = {}
#         url = ""
#         return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://38f61a2f.eu-gb.apigw.appdomain.cloud/api/dealership"
        dealerships = get_dealers_from_cf(url)
        context["dealerships_list"] = dealerships
        #context = {"dealerships": dealerships}
    return render(request, 'djangoapp/index.html', context)

def get_dealer_details(request, dealer_id):
    """ Dealerships Details """
    if request.method == "GET":
        context = {}
        dealer_url = "https://38f61a2f.eu-gb.apigw.appdomain.cloud/api/dealership"
        dealer_details = get_dealer_by_id_from_cf(dealer_url, dealer_id)
        # context = {
        #     "dealer_id": dealer_id,
        #     "full_name": full_name,
        #     "reviews": dealer_reviews
        # }
        context["dealer"] = dealer

        reviews_url = "https://38f61a2f.eu-gb.apigw.appdomain.cloud/api/reviews"
        dealer_reviews = get_dealer_reviews_from_cf(dealer_url,dealer_id)
        print(dealer_reviews)
        context["dealer_reviews"] = dealer_reviews
        dealer_details_view = render(
            request, 'djangoapp/dealer_details.html', context)

        # ADd here endpoint for dealer reviews! and details!
    return dealer_details_view

# Create a `add_review` view to submit a review


def add_dealer_review(request, dealer_id, dealer_name):
    """ Add Review View """
    context = {}
    dealer_url = "https://38f61a2f.eu-gb.apigw.appdomain.cloud/api/dealership"
    if request.method == "GET":
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context = {"cars": cars, "dealer_id": dealer_id,
                   "dealer_name": dealer_name}
        add_review_view = render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST" and request.user.is_authenticated:
        form = request.POST
        review = {
            "review_id": random.randint(0, 100),
            "reviewer_name": form["fullname"],
            "dealership": dealer_id,
            "review": form["review"]
        }
        if form.get("purchase"):
            review["purchase"] = True
            review["purchase_date"] = form["purchasedate"]
            car = get_object_or_404(CarModel, pk=form["car"])
            review["car_make"] = car.carmake.name
            review["car_model"] = car.name
            review["car_year"] = car.year
        json_result = add_dealer_review_to_db(review)
        add_review_view = redirect(
            'djangoapp:dealer_reviews', dealer_id=dealer_id, dealer_name=dealer_name)
    return add_review_view
