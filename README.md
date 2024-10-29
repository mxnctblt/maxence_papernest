<h1 align="center">Backend developer technical test</h1>
<h4 align="center">A test for Papernest.</h4>
<p align="center">
  <a href="#instructions">Instructions</a> •
  <a href="#technologies-used">Technologies Used</a> •
  <a href="#setup-and-installation">Setup and Installation</a> •
  <a href="#api-endpoints">API Endpoints</a> •
  <a href="#testing">Testing</a> •
  <a href="#error-handling">Error Handling</a> •
  <a href="#additional-notes">Additional Notes</a> •
  <a href="#author">Author</a>
</p>

## Instructions

💡 Papernest product team wants to start selling mobile phone contracts in our web app. In order to help users choose the best provider, we want to provide hints with the network coverage at home. We want to implement it on a separate web service.

#### Goal

Build a small api project that we can request with a textual address request and retrieve 2G/3G/4G network coverage for each operator (if available) in the response.

#### Example

GET: `your_api/?q=42+rue+papernest+75011+Paris`
Response:

```
{
	"orange": {"2G": true, "3G": true, "4G": false},
	"SFR": {"2G": true, "3G": true, "4G": true}
}
```

#### Data that you can use

[2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv](.2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv)
The file above provides a list of network coverage measure. Each line have the provider (20801 = Orange, 20810 = SFR, 20815 = Free, 20820 = Bouygue, [source](https://fr.wikipedia.org/wiki/Mobile_Network_Code#Tableau_des_MNC_pour_la_France_m%C3%A9tropolitaine)), Lambert93 geographic coordinate (X, Y) and network coverage for 2G, 3G and 4G

https://adresse.data.gouv.fr/api This API allow you to retrieve :

- address detail from a query address (the insee code, geographic coordinates, etc.)
- Do reverse geographic search (from longitude and latitude, retrieve an address).

##### Instructions:

- Use the language/framework/technology of your choice
- Provide the resulting source code **in a hosted git repository (public is allowed)**
- How you manage these data sources is up to you. Do as you want (you can use other data sources if you want).
- If you transform the csv file with some offline processing, please provide the source file.
- The goal is not to work on precise geographic match, a city-level precision is enough.
- The api interface (payload format) can be changed if you want.

#### Appendix

Convert from Lambert 93 to GPS coordinates can be a pain. The following code converts from the two coordinates system in Python using [pyproj](https://pypi.org/project/pyproj/) library

```
import pyproj

def lamber93_to_gps(x, y):
	lambert = pyproj.Proj('+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs')
	wgs84 = pyproj.Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
	x = 102980
	y = 6847973
	long, lat = pyproj.transform(lambert, wgs84, x, y)
	return long, lat
```

## Technologies Used

[Python](https://www.python.org/): Programming language.
[Django](https://www.djangoproject.com/): Web framework used for building the API.
Django REST Framework: Toolkit for building Web APIs in Django.
Pandas: Library used for data manipulation and analysis.
Requests: Library for making HTTP requests to external APIs.
[PyProj](https://pypi.org/project/pyproj/): Library for cartographic projections and coordinate transformations.

## Setup and Installation

#### Prerequisites:

- [Git](https://git-scm.com/)
- [Django](https://www.djangoproject.com/) 4.2
- [Python](https://www.python.org/) 3.8+
- pip (Python package installer)

#### Installation Steps

1. Clone the repository:

```
git clone https://github.com/mxnctblt/maxence_papernest.git
cd maxence_papernest
```

2. Install required packages (if not already done):

```
pip install django djangorestframework requests pandas pyproj
```

3. Set up environment variables:

Create a .env file in the root of the project and add your configuration.

4. Run migrations:

```
python manage.py migrate
```

5. Run the server:

```
python manage.py runserver
```

## API Endpoints

#### Retrieve Network Coverage

- Endpoint: http://127.0.0.1:8000/api/coverage/
- Method: GET
- Query Parameter:
  - q (string): The address to search for (e.g., 42 rue papernest 75011 Paris).
- Response:
  - Success (200): Returns a JSON object with network availability (2G, 3G, 4G) for each operator.
  - Error (400): Returns an error message if the query parameter q is missing.
  - Error (404): Returns an error message if no valid addresses are found.
  - Error (503): Returns an error message for connection issues with the address API.
  - Error (504): Returns an error message if the address API request times out.

#### Example Request

```
GET http://127.0.0.1:8000/api/coverage/?q=42+Rue+Pétion+75011+Paris
```

#### Example Response (Success)

```
{
    "orange": {"2G": true, "3G": true, "4G": true},
    "SFR": {"2G": true, "3G": true, "4G": true},
    "Bouygues": {"2G": false, "3G": false, "4G": false},
    "Free": {"2G": false, "3G": true, "4G": true}
}
```

#### Example Response (Error)

```
{
    "error": "No valid addresses found, please check the address."
}
```

## Testing

The project includes a set of unit tests to ensure the functionality of the API. To run the tests:

```
python manage.py test
```

Test Cases Include:

- Valid address queries.
- Invalid address queries.
- Queries with missing parameters.
- Edge cases with special characters and common street names.

## Error Handling

The API handles various error scenarios, including:

- Missing query parameters.
- No valid addresses found.
- Connection errors with the external address API.
- Timeout errors when requesting the external address API.

## Additional Notes

- Please ensure that you have the necessary permissions and API access when deploying the application.
- The CSV file processed used for network coverage data should be in the root directory as [processed_network_coverage.csv](processed_network_coverage.csv).
- The initial CSV file can be processed using the included script to convert the coordinates from Lambert 93 to WGS84 format if necessary. [process_csv.py](process_csv.py)

## Author

> Maxence Thibault [@mxnctblt](https://github.com/mxnctblt)
