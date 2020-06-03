from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

# An Asset is what a User books, the physical/ software/ service a Business provides
class Asset(models.Model):
    # The owner(Business) of the Asset
    business_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asset_owner',blank=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.TextField(default='')

    # Fields to store data for availability each day by hour (24 Hour Time)
    hour_start = models.IntegerField(default=0)
    hour_end = models.IntegerField(default=24)

    # Fields to store Availability each week by day
    mon_available = models.BooleanField(default=True)
    tue_available = models.BooleanField(default=True)
    wed_available = models.BooleanField(default=True)
    thu_available = models.BooleanField(default=True)
    fri_available = models.BooleanField(default=True)
    sat_available = models.BooleanField(default=True)
    sun_available = models.BooleanField(default=True)

    # Fields to store bookings made for Asset
    mon_bookings = models.TextField(default='')
    tue_bookings = models.TextField(default='')
    wed_bookings = models.TextField(default='')
    thu_bookings = models.TextField(default='')
    fri_bookings = models.TextField(default='')
    sat_bookings = models.TextField(default='')
    sun_bookings = models.TextField(default='')

    # Fields to store temporary data for each new booking
    book_start = models.IntegerField(default=0)
    book_end = models.IntegerField(default=0)
    choose_day = models.TextField(default='')

    def get_absolute_url(self):
        return reverse('table-bookingtable', kwargs={'pk': self.pk})


class Booking(models.Model):
    # The Asset that is booked
    business_asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    # The user that booked it
    user_booker = models.ForeignKey(User, on_delete=models.CASCADE,related_name='booker')

    # The time it was booked for, stored as 'HH:HH' e.g '10:22' and 'DAY' e.g 'Monday'
    booking_time = models.TextField(default='')
    booking_day = models.TextField(default='')

    def __str__(self):
        return str(self.id) + '| ' + self.booking_time + ' - ' + self.booking_day + ' for: ' + str(self.business_asset.title) + ' by: ' + str(self.user_booker.username)
