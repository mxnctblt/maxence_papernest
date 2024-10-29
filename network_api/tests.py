from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class NetworkCoverageTests(APITestCase):
    
    def test_no_valid_address_found(self):
        """Test when a non-existing address is queried, expecting no valid addresses."""
        response = self.client.get(reverse('network_coverage'), {'q': '42 rue papernest 75011 Paris'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "No valid addresses found, please check the address."})

    def test_wrong_address(self):
        """Test for an invalid address which should return no valid address found."""
        response = self.client.get(reverse('network_coverage'), {'q': 'this is a wrong address'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "No valid addresses found, please check the address."})

    def test_valid_address_with_coverage(self):
        """Test for a valid address that has coverage data, expecting a successful response."""
        response = self.client.get(reverse('network_coverage'), {'q': '42 Rue Pétion 75011 Paris'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('orange', response.data)
        self.assertIn('SFR', response.data)
        self.assertIn('Bouygues', response.data)
        self.assertIn('Free', response.data)

    def test_special_characters_in_address(self):
        """Test for an address with special characters."""
        response = self.client.get(reverse('network_coverage'), {'q': '42 Rue de l\'Orillon 75011 Paris'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_common_street_name(self):
        """Test for a common street name that might return multiple results."""
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
