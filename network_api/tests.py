from django.urls import reverse
from network_api.models import NetworkCoverage
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

class NetworkCoverageTests(APITestCase):
    
    def setUp(self):
        # Sample data for coverage, saved only in the test database
        NetworkCoverage.objects.create(operator='orange', longitude=-5.088856, latitude=48.456574, g2=True, g3=True, g4=False)
        NetworkCoverage.objects.create(operator='SFR', longitude=-5.088018, latitude=48.462854, g2=True, g3=True, g4=False)
        NetworkCoverage.objects.create(operator='Bouygues', longitude=-5.088009, latitude=48.462882, g2=True, g3=True, g4=True)
        NetworkCoverage.objects.create(operator='Free', longitude=-5.088856, latitude=48.456574, g2=True, g3=True, g4=True)

    @patch('requests.get')
    def test_no_valid_address_found(self, mock_get):
        """Test when a non-existing address is queried, expecting no valid addresses."""
        mock_get.return_value.json.return_value = {"features": []}

        response = self.client.get(reverse('network_coverage'), {'q': '42 rue papernest 75011 Paris'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "No valid addresses found, please check the address."})

    @patch('requests.get')
    def test_wrong_address(self, mock_get):
        """Test for an invalid address which should return no valid address found."""
        mock_get.return_value.json.return_value = {"features": []}

        response = self.client.get(reverse('network_coverage'), {'q': 'this is a wrong address'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "No valid addresses found, please check the address."})

    @patch('requests.get')
    def test_valid_address_with_coverage(self, mock_get):
        """Test for a valid address that has coverage data, expecting a successful response."""
        mock_get.return_value.json.return_value = {
            "features": [{
                "properties": {"score": 0.8},
                "geometry": {"coordinates": [-5.088856, 48.456574]}
            }]
        }

        response = self.client.get(reverse('network_coverage'), {'q': '42 Rue Pétion 75011 Paris'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Validate that each operator's data is returned
        expected_operators = ['orange', 'SFR', 'Bouygues', 'Free']
        for operator in expected_operators:
            self.assertIn(operator, response.data)
            self.assertIn('2G', response.data[operator])
            self.assertIn('3G', response.data[operator])
            self.assertIn('4G', response.data[operator])

    @patch('requests.get')
    def test_special_characters_in_address(self, mock_get):
        """Test for an address with special characters."""
        mock_get.return_value.json.return_value = {
            "features": [{
                "properties": {"score": 0.8},
                "geometry": {"coordinates": [-5.088856, 48.456574]}
            }]
        }  # Mock a valid response for address with special characters

        response = self.client.get(reverse('network_coverage'), {'q': '42 Rue de l\'Orillon 75011 Paris'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('requests.get')
    def test_common_street_name(self, mock_get):
        """Test for a common street name that might return multiple results."""
        mock_get.return_value.json.return_value = {
            "features": [{
                "properties": {"score": 0.9},
                "geometry": {"coordinates": [-5.088856, 48.456574]}
            }, {
                "properties": {"score": 0.85},
                "geometry": {"coordinates": [-5.088018, 48.462854]}
            }]
        }  # Mock multiple results for a common street name

        response = self.client.get(reverse('network_coverage'), {'q': 'Rue de Paris'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_missing_query_parameter(self):
        """Test for missing the 'q' query parameter, expecting a bad request response."""
        response = self.client.get(reverse('network_coverage'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            "error": "The address is missing. Query parameter 'q' is required. "
                      "Example: http://127.0.0.1:8000/api/coverage/?q=42+rue+papernest+75011+Paris"
        })

    def test_invalid_url(self):
        """Test for accessing an invalid URL, expecting a not found response."""
        response = self.client.get('/api/cove')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
