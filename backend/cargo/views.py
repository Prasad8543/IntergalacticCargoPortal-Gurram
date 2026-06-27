from django.db.models import Case, IntegerField, Q, Sum, Value, When
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination import DefaultPageNumberPagination

from .models import CargoRecord
from .parsers import parse_manifest
from .permissions import AdminUploadPermission
from .serializers import CargoRecordSerializer


class UploadManifestView(APIView):
    permission_classes = [IsAuthenticated, AdminUploadPermission]
    parser_classes = [MultiPartParser]

    def post(self, request):
        manifest = request.FILES.get('manifest')
        if manifest is None:
            return Response(
                {'error': 'manifest.txt file is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content = manifest.read().decode('utf-8')
        records, skipped = parse_manifest(content)

        saved = []
        for record in records:
            obj = CargoRecord.objects.create(
                cargo_id=record['cargo_id'],
                destination=record['destination'],
                weight_kg=record['weight_kg'],
                uploaded_by=request.user,
            )
            saved.append(obj)

        serializer = CargoRecordSerializer(saved, many=True)
        return Response(
            {
                'message': f'Imported {len(saved)} cargo record(s).',
                'saved': serializer.data,
                'skipped': skipped,
            },
            status=status.HTTP_201_CREATED,
        )


class CargoListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPageNumberPagination
    serializer_class = CargoRecordSerializer
    ordering_fields = ['weight_kg', 'created_at']
    ordering = ['-weight_kg']

    def get_queryset(self):
        queryset = CargoRecord.objects.all()
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(cargo_id__icontains=search) | Q(destination__icontains=search)
            )

        ordering = self.request.query_params.get('ordering', self.ordering[0])
        allowed = set()
        for field in self.ordering_fields:
            allowed.add(field)
            allowed.add(f'-{field}')
        if ordering not in allowed:
            ordering = self.ordering[0]

        return queryset.annotate(
            earth_last=Case(
                When(destination__icontains='Earth', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('earth_last', ordering, 'id')


class CargoStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = CargoRecord.objects.all()
        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(cargo_id__icontains=search) | Q(destination__icontains=search)
            )

        return Response(
            {
                'total_cargo': queryset.count(),
                'destinations': queryset.values('destination').distinct().count(),
                'total_weight_kg': queryset.aggregate(total=Sum('weight_kg'))['total'] or 0,
                'sector7_count': queryset.filter(destination__icontains='Sector-7').count(),
            }
        )
