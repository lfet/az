from django.urls import path
from django.conf.urls import url, include
from .views import BookingRudView

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', BookingRudView.as_view(), name='post-rud'),
    ]

