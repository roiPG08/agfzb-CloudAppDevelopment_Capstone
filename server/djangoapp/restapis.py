import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    api_key = kwargs.get("api_key")
    print("GET from {} ".format(url))
    try:
        if api_key:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

def post_request(url, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    print(payload)
    response = requests.post(url, params=kwargs, json=payload)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    state = kwargs.get("state")
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["body"]["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results
# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def get_dealersby_state(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_by_id_from_cf(url, dealerId):
    json_result = get_request(url)
    if json_result:
        dealers = json_result["body"]
        
    
        dealer_doc = dealers["docs"][0]
        dealer_obj = CarDealer(full_name=dealer_doc["full_name"], short_name=dealer_doc["short_name"], address=dealer_doc["address"], city=dealer_doc["city"],
                                id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                state=dealer_doc["state"],
                                st=dealer_doc["st"], zip=dealer_doc["zip"])
    return dealer_obj

# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list

def get_dealer_reviews_from_cf(dealerId):
    """ Get Reviews"""
    results = []
    json_result = get_request(API_URL_REVIEW, dealerId=dealerId)
    if json_result:
        reviews = json_result["entries"]
        for review in reviews:
            sentiment = analyze_review_sentiments(review["review"])
            dealer_review = DealerReview(id=review["id"],
                                         name=review["name"],
                                         dealership=review["dealership"],
                                         review=review["review"],
                                         purchase=review["purchase"],
                                         purchase_date=review["purchase_date"],
                                         car_make=review["car_make"],
                                         car_model=review["car_model"],
                                         car_year=review["car_year"],
                                         sentiment=sentiment)
            results.append(dealer_review)
    return results


def add_dealer_review_to_db(review_post):
    """ Add Review """
    review = {
        "id": review_post['review_id'],
        "name": review_post['reviewer_name'],
        "dealership": review_post['dealership'],
        "review": review_post['review'],
        "purchase": review_post.get('purchase', False),
        "purchase_date": review_post.get('purchase_date'),
        "car_make": review_post.get('car_make'),
        "car_model": review_post.get('car_model'),
        "car_year": review_post.get('car_year')
    }
    return post_request(API_URL_REVIEW, review)

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text


def analyze_review_sentiments(text):
    """ Sentiment Analyze """
    json_result = get_request(API_URL_SENTIMENT, text=text)
    if json_result:
        sentiment_result = json_result.get('label', 'neutral')
    return sentiment_result

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative



