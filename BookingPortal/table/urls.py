from django.urls import path
from . import views
from .views import BookingListView

urlpatterns = [
    path('', views.home, name='table-h'),
    path('dashboard/', views.dashboard, name='table-dashboard'),
    path('dashboard/createasset', views.asset_create_view, name='table-asset_form'),
    path('dashboard/viewbookings', BookingListView.as_view(), name='table-viewbookings'),
    path('dashboard/searchbusinesses', views.SearchBusinesses, name='table-searchbusinesses'),
    path('dashboard/viewbookingtables/<owner>', views.assetlist, name='table-viewbookingtables'),
    path('dashboard/<owner>/<asset>/bookingtable', views.bookingtable, name='table-bookingtable'),
    path('dashboard/<owner>/<asset>/makebooking', views.AssetMakeBooking, name='table-asset_form'),
    path('dashboard/<owner>/<asset>/delete/<int:pk>', views.delete_asset_view, name='table-asset_delete'),
    path('dashboard/<owner>/<asset>/update/<int:pk>', views.update_asset_view, name='table-asset_update'),
    path('dashboard/viewbookings/<int:pk>/delete', views.delete_booking_view, name='table-deletebooking'),
    ]

