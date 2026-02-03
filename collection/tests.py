import io
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Account, Consumer


class ModelTests(TestCase):
    def test_consumer_creation(self):
        consumer = Consumer.objects.create(
            name='John Doe',
            address='123 Main St',
            ssn='123-45-6789'
        )
        self.assertEqual(str(consumer), 'John Doe')
        self.assertEqual(consumer.ssn, '123-45-6789')

    def test_account_creation(self):
        account = Account.objects.create(
            client_reference='test-ref-001',
            balance=Decimal('1000.50'),
            status='IN_COLLECTION'
        )
        self.assertEqual(str(account), 'test-ref-001')
        self.assertEqual(account.balance, Decimal('1000.50'))

    def test_account_consumer_relationship(self):
        consumer1 = Consumer.objects.create(
            name='John Doe',
            address='123 Main St',
            ssn='123-45-6789'
        )
        consumer2 = Consumer.objects.create(
            name='Jane Doe',
            address='456 Oak Ave',
            ssn='987-65-4321'
        )
        account = Account.objects.create(
            client_reference='test-ref-001',
            balance=Decimal('5000.00'),
            status='IN_COLLECTION'
        )
        account.consumers.add(consumer1, consumer2)

        self.assertEqual(account.consumers.count(), 2)
        self.assertIn(consumer1, account.consumers.all())
        self.assertIn(consumer2, account.consumers.all())


class AccountListViewTests(APITestCase):
    def setUp(self):
        """Set up test data."""
        self.consumer1 = Consumer.objects.create(
            name='John Smith',
            address='123 Main St',
            ssn='111-11-1111'
        )
        self.consumer2 = Consumer.objects.create(
            name='Jane Doe',
            address='456 Oak Ave',
            ssn='222-22-2222'
        )
        self.consumer3 = Consumer.objects.create(
            name='Bob Johnson',
            address='789 Pine Rd',
            ssn='333-33-3333'
        )

        self.account1 = Account.objects.create(
            client_reference='ref-001',
            balance=Decimal('100.00'),
            status='IN_COLLECTION'
        )
        self.account1.consumers.add(self.consumer1)

        self.account2 = Account.objects.create(
            client_reference='ref-002',
            balance=Decimal('500.00'),
            status='PAID_IN_FULL'
        )
        self.account2.consumers.add(self.consumer2)

        self.account3 = Account.objects.create(
            client_reference='ref-003',
            balance=Decimal('1000.00'),
            status='INACTIVE'
        )
        self.account3.consumers.add(self.consumer3)

        self.account4 = Account.objects.create(
            client_reference='ref-004',
            balance=Decimal('2500.00'),
            status='IN_COLLECTION'
        )
        self.account4.consumers.add(self.consumer1, self.consumer2)

    def test_list_all_accounts(self):
        response = self.client.get('/accounts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)

    def test_filter_by_min_balance(self):
        response = self.client.get('/accounts/', {'min_balance': '500'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_filter_by_max_balance(self):
        response = self.client.get('/accounts/', {'max_balance': '500'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_by_balance_range(self):
        response = self.client.get('/accounts/', {
            'min_balance': '100',
            'max_balance': '1000'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_filter_by_consumer_name(self):
        response = self.client.get('/accounts/', {'consumer_name': 'john'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_filter_by_status(self):
        response = self.client.get('/accounts/', {'status': 'IN_COLLECTION'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_by_status_case_insensitive(self):
        response = self.client.get('/accounts/', {'status': 'in_collection'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_combined_filters(self):
        response = self.client.get('/accounts/', {
            'min_balance': '100',
            'max_balance': '1000',
            'status': 'IN_COLLECTION'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_invalid_min_balance(self):
        response = self.client.get('/accounts/', {'min_balance': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_invalid_max_balance(self):
        response = self.client.get('/accounts/', {'max_balance': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_invalid_status(self):
        response = self.client.get('/accounts/', {'status': 'INVALID_STATUS'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_pagination(self):
        for i in range(15):
            account = Account.objects.create(
                client_reference=f'ref-extra-{i}',
                balance=Decimal('100.00'),
                status='IN_COLLECTION'
            )
            account.consumers.add(self.consumer1)

        response = self.client.get('/accounts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], 19)
        self.assertIsNotNone(response.data['next'])

    def test_pagination_page_size(self):
        response = self.client.get('/accounts/', {'page_size': '2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)


class CSVUploadViewTests(APITestCase):
    def test_upload_csv_success(self):
        csv_content = (
            'client reference no,balance,status,consumer name,consumer address,ssn\n'
            'ref-001,1000.00,IN_COLLECTION,John Doe,123 Main St,111-11-1111\n'
            'ref-002,2000.00,PAID_IN_FULL,Jane Doe,456 Oak Ave,222-22-2222\n'
        )
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'test.csv'

        response = self.client.post(
            '/accounts/upload/',
            {'file': csv_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['accounts_created'], 2)
        self.assertEqual(response.data['consumers_created'], 2)
        self.assertEqual(Account.objects.count(), 2)
        self.assertEqual(Consumer.objects.count(), 2)

    def test_upload_csv_no_file(self):
        response = self.client.post('/accounts/upload/', {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_upload_non_csv_file(self):
        txt_file = io.BytesIO(b'not a csv')
        txt_file.name = 'test.txt'

        response = self.client.post(
            '/accounts/upload/',
            {'file': txt_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_upload_csv_missing_columns(self):
        csv_content = 'name,balance\nJohn,1000\n'
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'test.csv'

        response = self.client.post(
            '/accounts/upload/',
            {'file': csv_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_csv_duplicate_handling(self):
        csv_content = (
            'client reference no,balance,status,consumer name,consumer address,ssn\n'
            'ref-001,1000.00,IN_COLLECTION,John Doe,123 Main St,111-11-1111\n'
            'ref-001,1000.00,IN_COLLECTION,Jane Doe,456 Oak Ave,222-22-2222\n'
        )
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'test.csv'

        response = self.client.post(
            '/accounts/upload/',
            {'file': csv_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['accounts_created'], 1)
        self.assertEqual(response.data['consumers_created'], 2)

        account = Account.objects.get(client_reference='ref-001')
        self.assertEqual(account.consumers.count(), 2)
