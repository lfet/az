from rest_framework import generics
from table.models import Booking
from .serializers import BookingSerializer


class BookingRudView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    serializer_class = BookingSerializer
    # queryset = Booking.objects.all()

    def get_queryset(self):
        return Booking.objects.all()

    # def get_object(self):
    #     pk = self.kwargs.get("pk")
    #     return Booking.objects.all()s