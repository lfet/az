from rest_framework import serializers
from table.models import Booking, Asset
from table.views import check_bookings_helper

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'pk',
            'business_asset',
            'user_booker',
            'booking_time',
            'booking_day',
        ]

        # read_only_fields = ['business_asset', 'user_booker']

    def validate(self, data):

        check = check_bookings_helper(data['business_asset'],data['booking_time'],data['booking_day'])
        asset = data['business_asset']

        st = int(data['booking_time'].split(":")[0])
        ft = int(data['booking_time'].split(':')[1])

        if st >= ft:
            raise serializers.ValidationError("Start time is before finish time!")
        elif st >= asset.hour_end or ft <= asset.hour_start:
            raise serializers.ValidationError("Booking is not within booking hours!")
        elif not check:
            raise serializers.ValidationError("Booking for that time is already made :(")
        else:
            raise serializers.ValidationError("Booking for that time is already made :(")
            return data

        # converts to JSON
        # validations for data passed
