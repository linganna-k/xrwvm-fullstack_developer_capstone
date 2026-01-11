import json
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import (
    analyze_review_sentiments,
    get_request,
    post_review,
)

# Get an instance of a logger
logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    """Handle user login."""
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]

    user = authenticate(username=username, password=password)
    response = {"userName": username}

    if user is not None:
        login(request, user)
        response["status"] = "Authenticated"

    return JsonResponse(response)


def logout_request(request):
    """Handle user logout."""
    logout(request)
    return JsonResponse({"userName": ""})


@csrf_exempt
def registration(request):
    """Handle user registration."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)

    username = data["userName"]
    password = data["password"]
    first_name = data["firstName"]
    last_name = data["lastName"]
    email = data["email"]

    if User.objects.filter(username=username).exists():
        return JsonResponse(
            {"userName": username, "error": "Already Registered"}
        )

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )

    login(request, user)

    return JsonResponse(
        {"userName": username, "status": "Authenticated"}
    )


def get_cars(request):
    """Return list of car makes and models."""
    if CarMake.objects.count() == 0:
        initiate()

    car_models = CarModel.objects.select_related("car_make")
    cars = [
        {
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name,
        }
        for car_model in car_models
    ]

    return JsonResponse({"CarModels": cars})


def get_dealerships(request, state="All"):
    """Return dealerships (all or by state)."""
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"

    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_reviews(request, dealer_id):
    """Return reviews for a dealer with sentiment analysis."""
    if not dealer_id:
        return JsonResponse(
            {"status": 400, "message": "Bad Request"}
        )

    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint)

    for review in reviews:
        sentiment = analyze_review_sentiments(review["review"])
        review["sentiment"] = sentiment.get("sentiment")

    return JsonResponse({"status": 200, "reviews": reviews})


def get_dealer_details(request, dealer_id):
    """Return dealer details."""
    if not dealer_id:
        return JsonResponse(
            {"status": 400, "message": "Bad Request"}
        )

    endpoint = f"/fetchDealer/{dealer_id}"
    dealership = get_request(endpoint)

    return JsonResponse({"status": 200, "dealer": dealership})


def add_review(request):
    """Submit a review."""
    if request.user.is_anonymous:
        return JsonResponse(
            {"status": 403, "message": "Unauthorized"}
        )

    try:
        data = json.loads(request.body)
        post_review(data)
        return JsonResponse({"status": 200})
    except (json.JSONDecodeError, KeyError):
        return JsonResponse(
            {"status": 401, "message": "Error in posting review"}
        )
