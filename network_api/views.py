from django.conf import settings
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import logging
import pandas as pd
import requests

# Set up logging for debugging and error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the pre-processed CSV file into a DataFrame
coverage_data = pd.read_csv('processed_network_coverage.csv')

# Define constants
SCORE_THRESHOLD = 0.7
ADDRESS_API_URL = 'https://api-adresse.data.gouv.fr/search/'

@api_view(['GET'])
def network_coverage(request):
    """
    Retrieve network coverage for a specified address.
    
    This view takes an address query parameter and returns a JSON response
    indicating the network availability (2G, 3G, 4G) for each operator.
    
    Parameters:
    - q (str): Address to search for (e.g., '42 rue papernest 75011 Paris').

    Returns:
    - JSON response containing network availability for each operator if found,
      or an error message if no valid addresses are found.
    """
    query = request.GET.get('q')
    
    # Check if the query parameter 'q' is provided
    if not query:
        error_message = {
            "error": "The address is missing. Query parameter 'q' is required. "
                      "Example: http://127.0.0.1:8000/api/coverage/?q=42+rue+papernest+75011+Paris"
        }
        logger.warning("Missing query parameter: %s", query)
        return Response(error_message, status=400)

    # Use the API to get coordinates from the address
    try:
        response = requests.get(f'{ADDRESS_API_URL}?q={query}&limit=5', timeout=5)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
    except requests.HTTPError as http_err:
        logger.error("Address API HTTP error: %s", str(http_err))
        return Response({"error": "Error while communicating with the address API."}, status=response.status_code)
    except requests.ConnectionError:
        logger.error("Address API connection error.")
        return Response({"error": "Failed to connect to the address API."}, status=503)
    except requests.Timeout:
        logger.error("Address API request timed out.")
        return Response({"error": "Address API request timed out."}, status=504)
    except Exception as e:
        logger.error("Address API request failed: %s", str(e))
        return Response({"error": f"Address API request failed: {str(e)}"}, status=500)

    # Filter results based on score to find valid addresses
    valid_features = [feature for feature in data['features'] if feature['properties']['score'] > SCORE_THRESHOLD]

    # If no valid addresses found, log and return an error
    if not valid_features:
        logger.info("No valid addresses found for query: %s", query)
        return Response({"error": "No valid addresses found, please check the address."}, status=404)

    # Extract coordinates from the first valid match
    coords = valid_features[0]['geometry']['coordinates']
    longitude, latitude = coords

    # Initial search ranges for local precision
    search_ranges = [0.01, 0.02, 0.05, 0.1]

    # Search for coverage data within defined ranges
    for search_range in search_ranges:
        # Filter DataFrame within the current range
        coverage_results = coverage_data[
            (coverage_data['longitude'].between(longitude - search_range, longitude + search_range)) &
            (coverage_data['latitude'].between(latitude - search_range, latitude + search_range))
        ]

        # If coverage data is found, format the result
        if not coverage_results.empty:
            result = {}
            for _, row in coverage_results.iterrows():
                operator = row['Operator']
                result[operator] = {
                    '2G': bool(row['2G']),
                    '3G': bool(row['3G']),
                    '4G': bool(row['4G'])
                }
            return Response(result)

    # If no data found within any range, return a message indicating no coverage
    logger.info("No network coverage information available for coordinates: (%f, %f)", latitude, longitude)
    return Response({"message": "No network coverage information is available for this area."})
