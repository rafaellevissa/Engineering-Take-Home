import csv
import io
from decimal import Decimal, InvalidOperation

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Account, Consumer
from .serializers import AccountSerializer


class AccountPagination(PageNumberPagination):
    """
    Page number pagination for accounts.

    Pros:
    - Simple to use and understand
    - Allows jumping to specific pages
    - Good for UI with page numbers

    Cons:
    - Can have inconsistent results if data changes between requests
    - Not ideal for very large datasets (counting total pages is expensive)
    - Page numbers can shift when items are added/deleted
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class AccountListView(APIView):
    pagination_class = AccountPagination

    def get(self, request):
        queryset = Account.objects.all().prefetch_related('consumers').order_by('-balance')

        min_balance = request.query_params.get('min_balance')
        if min_balance:
            try:
                min_balance = Decimal(min_balance)
                queryset = queryset.filter(balance__gte=min_balance)
            except InvalidOperation:
                return Response(
                    {'error': 'Invalid min_balance value'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        max_balance = request.query_params.get('max_balance')
        if max_balance:
            try:
                max_balance = Decimal(max_balance)
                queryset = queryset.filter(balance__lte=max_balance)
            except InvalidOperation:
                return Response(
                    {'error': 'Invalid max_balance value'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        consumer_name = request.query_params.get('consumer_name')
        if consumer_name:
            queryset = queryset.filter(consumers__name__icontains=consumer_name).distinct()

        account_status = request.query_params.get('status')
        if account_status:
            account_status = account_status.upper()
            valid_statuses = [choice[0] for choice in Account.STATUS_CHOICES]
            if account_status not in valid_statuses:
                return Response(
                    {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            queryset = queryset.filter(status=account_status)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = AccountSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = AccountSerializer(queryset, many=True)
        return Response(serializer.data)


class CSVUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided. Please upload a CSV file.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        csv_file = request.FILES['file']

        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV file.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            accounts_created = 0
            consumers_created = 0

            for row in reader:
                consumer, created = Consumer.objects.get_or_create(
                    ssn=row['ssn'],
                    defaults={
                        'name': row['consumer name'],
                        'address': row['consumer address'],
                    }
                )
                if created:
                    consumers_created += 1

                account, created = Account.objects.get_or_create(
                    client_reference=row['client reference no'],
                    defaults={
                        'balance': row['balance'],
                        'status': row['status'],
                    }
                )
                if created:
                    accounts_created += 1

                account.consumers.add(consumer)

            return Response({
                'message': 'CSV file processed successfully.',
                'accounts_created': accounts_created,
                'consumers_created': consumers_created,
            }, status=status.HTTP_201_CREATED)

        except KeyError as e:
            return Response(
                {'error': f'Missing required column: {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error processing CSV: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
