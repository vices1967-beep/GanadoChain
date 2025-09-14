from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Avg, Max, Min, Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

# Importaciones corregidas desde las ubicaciones correctas
from blockchain.market_models import MarketListing, Trade
from blockchain.serializers import (
    MarketListingSerializer, 
    TradeSerializer,
    CreateMarketListingSerializer,
    ExecuteTradeSerializer
)
from cattle.models import Animal
from cattle.serializers import AnimalSerializer
import logging

logger = logging.getLogger(__name__)

class MarketListingViewSet(viewsets.ModelViewSet):
    serializer_class = MarketListingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateMarketListingSerializer
        return MarketListingSerializer
    
    def get_queryset(self):
        queryset = MarketListing.objects.filter(is_active=True)
        
        # Filtros de búsqueda
        animal_id = self.request.query_params.get('animal_id')
        seller_id = self.request.query_params.get('seller_id')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        currency = self.request.query_params.get('currency')
        breed = self.request.query_params.get('breed')
        
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if currency:
            queryset = queryset.filter(currency=currency)
        if breed:
            queryset = queryset.filter(animal__breed__icontains=breed)
            
        return queryset.order_by('-listing_date')
    
    def perform_create(self, serializer):
        animal = serializer.validated_data['animal']
        
        # Verificar que el usuario es el dueño del animal
        if animal.owner != self.request.user:
            raise PermissionError("Solo el dueño puede listar el animal")
        
        # Verificar que el animal no está ya listado
        if MarketListing.objects.filter(animal=animal, is_active=True).exists():
            raise PermissionError("Este animal ya está listado en el mercado")
        
        serializer.save(seller=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel_listing(self, request, pk=None):
        listing = self.get_object()
        
        if listing.seller != request.user:
            return Response(
                {'error': 'Solo el vendedor puede cancelar el listado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        listing.is_active = False
        listing.save()
        
        return Response({'success': True, 'message': 'Listado cancelado exitosamente'})
    
    @action(detail=False, methods=['get'])
    def my_listings(self, request):
        listings = MarketListing.objects.filter(seller=request.user)
        serializer = self.get_serializer(listings, many=True)
        return Response(serializer.data)

class TradeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Trade.objects.all()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(listing__seller=self.request.user) |
                Q(buyer=self.request.user)
            )
        
        # Filtros adicionales
        listing_id = self.request.query_params.get('listing_id')
        buyer_id = self.request.query_params.get('buyer_id')
        status_filter = self.request.query_params.get('status')
        
        if listing_id:
            queryset = queryset.filter(listing_id=listing_id)
        if buyer_id:
            queryset = queryset.filter(buyer_id=buyer_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-trade_date')
    
    @action(detail=False, methods=['get'])
    def my_trades(self, request):
        trades = Trade.objects.filter(
            Q(listing__seller=request.user) | Q(buyer=request.user)
        ).order_by('-trade_date')
        serializer = self.get_serializer(trades, many=True)
        return Response(serializer.data)

class MarketStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        active_listings = MarketListing.objects.filter(is_active=True)
        
        stats = {
            'total_listings': active_listings.count(),
            'total_trades': Trade.objects.count(),
            'total_volume': float(Trade.objects.aggregate(
                total=Sum('price'))['total'] or 0),
            'avg_price': float(active_listings.aggregate(
                avg=Avg('price'))['avg'] or 0),
            'max_price': float(active_listings.aggregate(
                max=Max('price'))['max'] or 0),
            'min_price': float(active_listings.aggregate(
                min=Min('price'))['min'] or 0),
            'listings_by_currency': dict(active_listings.values_list('currency').annotate(
                count=Count('id'))),
            'listings_by_breed': dict(active_listings.values_list('animal__breed').annotate(
                count=Count('id'))),
            'recent_trades': Trade.objects.filter(
                trade_date__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
            'platform_fees': float(Trade.objects.aggregate(
                total=Sum('platform_fee'))['total'] or 0)
        }
        
        return Response(stats)

class PriceHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, animal_id=None):
        if animal_id:
            animal = get_object_or_404(Animal, id=animal_id)
            trades = Trade.objects.filter(listing__animal=animal).order_by('trade_date')
            
            data = [{
                'date': trade.trade_date.strftime('%Y-%m-%d'),
                'price': float(trade.price),
                'currency': trade.currency,
                'buyer': trade.buyer.username if trade.buyer else None,
                'trade_id': trade.id
            } for trade in trades]
            
            return Response({
                'animal': {
                    'id': animal.id,
                    'ear_tag': animal.ear_tag,
                    'breed': animal.breed
                },
                'price_history': data,
                'trade_count': len(data)
            })
        
        else:
            # Precios promedios por día (últimos 30 días)
            thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
            
            daily_prices = Trade.objects.filter(
                trade_date__gte=thirty_days_ago
            ).annotate(
                date=TruncDate('trade_date')
            ).values('date', 'currency').annotate(
                avg_price=Avg('price'),
                trade_count=Count('id'),
                total_volume=Sum('price')
            ).order_by('date')
            
            return Response({
                'daily_prices': list(daily_prices),
                'time_period': f'{thirty_days_ago.date()} to {timezone.now().date()}'
            })

class ExecuteTradeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, listing_id):
        listing = get_object_or_404(MarketListing, id=listing_id, is_active=True)
        
        serializer = ExecuteTradeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        buyer_wallet = serializer.validated_data['buyer_wallet']
        
        # Verificaciones
        if listing.seller == request.user:
            return Response(
                {'error': 'No puedes comprar tu propio listado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.wallet_address:
            return Response(
                {'error': 'Debes tener una wallet configurada para realizar compras'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Aquí iría la lógica de blockchain para ejecutar el trade
            # En producción, se conectaría con el contrato inteligente
            
            # Simulación de la transacción
            trade = Trade.objects.create(
                listing=listing,
                buyer=request.user,
                price=listing.price,
                currency=listing.currency,
                platform_fee=listing.price * 0.02,  # 2% de comisión
                status='COMPLETED',
                transaction_hash=f"0x{hash(str(timezone.now()) + str(listing_id))[:64]}"
            )
            
            # Desactivar el listado
            listing.is_active = False
            listing.save()
            
            # Transferir la propiedad del animal (esto sería en blockchain)
            animal = listing.animal
            animal.owner = request.user
            animal.save()
            
            return Response({
                'success': True,
                'message': 'Trade ejecutado exitosamente',
                'trade_id': trade.id,
                'amount': float(trade.price),
                'currency': trade.currency,
                'platform_fee': float(trade.platform_fee),
                'transaction_hash': trade.transaction_hash
            })
            
        except Exception as e:
            logger.error(f"Error ejecutando trade: {str(e)}")
            return Response(
                {'error': f'Error ejecutando trade: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

class AnimalMarketView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, animal_id):
        animal = get_object_or_404(Animal, id=animal_id)
        
        # Verificar permisos
        if animal.owner != request.user and not request.user.is_staff:
            return Response(
                {'error': 'No tienes permisos para ver este animal'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        market_data = {
            'animal': AnimalSerializer(animal).data,
            'current_listing': None,
            'trade_history': [],
            'price_suggestions': self.get_price_suggestions(animal)
        }
        
        # Obtener listado activo si existe
        active_listing = MarketListing.objects.filter(animal=animal, is_active=True).first()
        if active_listing:
            market_data['current_listing'] = MarketListingSerializer(active_listing).data
        
        # Obtener historial de trades
        trades = Trade.objects.filter(listing__animal=animal).order_by('-trade_date')
        market_data['trade_history'] = TradeSerializer(trades, many=True).data
        
        return Response(market_data)
    
    def get_price_suggestions(self, animal):
        # Sugerencias de precio basadas en trades similares
        similar_trades = Trade.objects.filter(
            listing__animal__breed=animal.breed
        ).aggregate(
            avg_price=Avg('price'),
            max_price=Max('price'),
            min_price=Min('price'),
            trade_count=Count('id')
        )
        
        return {
            'suggested_price': float(similar_trades['avg_price'] or 0),
            'price_range': {
                'min': float(similar_trades['min_price'] or 0),
                'max': float(similar_trades['max_price'] or 0)
            },
            'based_on_trades': similar_trades['trade_count'] or 0
        }