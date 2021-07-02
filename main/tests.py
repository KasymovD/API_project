from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from main.models import Category, Product

User = get_user_model()

class TestProduct(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(email='test@gmail.com', password='qwerty')
        self.user1 = User.objects.create(email='addirossi@gmail.com', password='qwerty', is_active=True)
        self.category1 = Category.objects.create(title='Телевизоры', slug='tv')
        self.product_payload = {
            'category': self.category1.slug,
            'title': 'Hisense 43"',
            'description': "Классный телик",
            'price': 20000
        }
        res1 = self.client.post('/api/v1/login/', data={
            'email': 'test@gmail.com',
            'password': 'qwerty'})
        self.admin_token = res1.data['token']
        res2 = self.client.post('/api/v1/login/', data={
            'email': 'addirossi@gmail.com',
            'password': 'qwerty'})
        self.user_token = res2.data['token']

        self.product1 = Product.objects.create(title='LG 42"',
                                               description='Крутой телевизор',
                                               price=25000.00,
                                               category=self.category1)
        self.product2 = Product.objects.create(title='Xiaomi"',
                                               description='Телевизор Node',
                                               price=20144.00,
                                               category=self.category1)
        self.product3 = Product.objects.create(title='Hisense 32"',
                                               description='Крутой телевизор',
                                               price=15000.00,
                                               category=self.category1)

    def test_product_create_by_anonymous_user(self):
        url = reverse('product-list')
        response = self.client.post(url, self.product_payload)
        self.assertEqual(response.status_code, 401)

    def test_product_create_by_simple_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token}')
        url = reverse('product-list')
        response = self.client.post(url, self.product_payload)
        self.assertEqual(response.status_code, 403)

    def test_product_create_by_admin_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        url = reverse('product-list')
        response = self.client.post(url, self.product_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], self.product_payload['title'])

    def test_product_create_without_category(self):
        product_data = self.product_payload.copy()
        product_data.pop('category')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        url = reverse('product-list')
        response = self.client.post(url, product_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('category', response.data)

    def test_product_create_without_description(self):
        product_data = self.product_payload.copy()
        product_data.pop('description')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        url = reverse('product-list')
        response = self.client.post(url, product_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('description', response.data)

    def test_product_create_without_price(self):
        product_data = self.product_payload.copy()
        product_data.pop('price')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        url = reverse('product-list')
        response = self.client.post(url, product_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('price', response.data)

    def test_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)

    def test_products_filter_by_price_from(self):
        filter_params = {'price_from': 20000}
        url = reverse('product-list')
        response = self.client.get(url, filter_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_update_product_by_anonymous_user(self):
        url = reverse('product-detail', args=[self.product1.id, ])
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 401)

    def test_update_product_by_simple_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token}')
        url = reverse('product-detail', args=[self.product1.id, ])
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 403)

    def test_update_product_by_admin_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        url = reverse('product-detail', args=[self.product1.id, ])
        update_data = {'price': 23000}
        response = self.client.patch(url, data=update_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['price'], '23000.00')

    def test_delete_product_by_anonymous_user(self):
        url = reverse('product-detail', args=[self.product2.id, ])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)

    def test_delete_product_by_simple_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token}')
        url = reverse('product-detail', args=[self.product2.id, ])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_delete_product_by_admin_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token}')
        url = reverse('product-detail', args=[self.product2.id, ])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
