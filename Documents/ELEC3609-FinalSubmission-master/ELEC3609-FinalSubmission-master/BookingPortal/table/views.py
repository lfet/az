from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django import forms
from .forms import AssetCreateForm, AssetBookForm, SearchBusinessesForm, AssetUpdateForm
from .models import Asset, Booking
from users.models import Profile
from django.contrib.auth.decorators import login_required

# Control to direct user when accessing root level of site
def home(request):
    # If user is signed in direct to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard/')
    # Else direct to login
    else:
        return redirect('login/')

# View to render Dashboard
@login_required
def dashboard(request):
    return render(request, 'table/dashboard.html', {'title': 'Dashboard', 'user': request.user})


# View to display list of User's bookings
class BookingListView(ListView):
    model = Booking
    context_object_name = 'bookings'


# View for Business to create an Asset
@login_required
def asset_create_view(request):

    # Find profile for current logged in User
    profile = Profile.objects.filter(user=request.user)

    # If User is not signed up as Business, then redirect to Dashboard
    if(profile[0].userType != 'Business'):
        return redirect('/dashboard')

    # If form is posted
    if request.method == 'POST':

        form = AssetCreateForm(request.POST)


        # If form is valid and the starting hour is before the ending hour
        if form.is_valid() and form.cleaned_data.get('hour_start') < form.cleaned_data.get('hour_end'):

            # add creator as the owner and then save
            asset = form.save(commit=True)
            asset.business_owner = request.user
            asset.save()

            messages.success(request, f'Asset: ' + form.cleaned_data.get('title') + '. Has been created!')

            return redirect('/dashboard/' + str(Asset.objects.all().last().business_owner.username) + '/' + str(Asset.objects.all().last().title) +'/bookingtable')

        elif form.is_valid():
            messages.warning(request, f'START TIME IS NOT BEFORE END TIME')
        else:
            messages.success(request, f'FordayBookingListInvalid!')

    else:
        form = AssetCreateForm()

    context = {
        'form': form,
        'title': 'Create Booking Table'
    }

    return render(request, 'table/asset_form.html', context)


# View for user to make Booking
@login_required
def AssetMakeBooking(request, owner, asset):

    # Find profile for current logged in User
    profile = Profile.objects.filter(user=request.user)

    # If User is not signed up as User, then redirect to send warning and/ or redirect back to Table
    if (profile[0].userType != 'User'):
        messages.warning(request,f'Business accounts can not make bookings. Please log out and sign up as a User to make bookings.')

        if request.method == 'POST':
            return redirect('/dashboard/' + owner + '/' + asset + '/bookingtable')

    # From url arguments passed in, find corrosponding asset by owner and asset title
    assets = Asset.objects.all()

    for a in assets:
        if a.business_owner != None:
            if a.business_owner.username == owner and a.title == asset:
                asset = a


    if request.method == 'POST':

        # pass in c (choices of days available to book) by calling helper function
        form = AssetBookForm(request.POST,c=get_available_days_helper(asset))

        if form.is_valid():

            # If the start of booking time is not before the end, display warning
            if form.cleaned_data.get('book_start') >= form.cleaned_data.get('book_end'):
                messages.warning(request, f'START TIME IS NOT BEFORE END TIME')

            # Check if booking time is within available hours
            elif form.cleaned_data.get('book_start') < asset.hour_start or form.cleaned_data.get('book_end') > asset.hour_end:
                messages.warning(request, f'START TIME IS NOT IN AVAILABLE BOOKING HOURS. (' + str(asset.hour_start) + ':00 - ' + str(asset.hour_end) + ':00)')

            else:
                bookingtime = str(form.cleaned_data.get('book_start')) + ':' + str(form.cleaned_data.get('book_end'))
                bookingday = form.cleaned_data.get('choose_day')
                # Call helper function to check if booking time is available

                # CHECK BOOKING AVAILABLE
                # CREATE NEW BOOKING

                check = check_bookings_helper(asset,bookingtime,bookingday)

                # If time not available helper function would have returned '', else returns day it was booked for.
                if check == False:
                    messages.warning(request, f'Booking time not available. Check booking table for availability')
                else:
                    Booking.objects.create(business_asset=asset, booking_time=bookingtime, booking_day=bookingday, user_booker=request.user)

                    messages.success(request, f'Booking made from ' + str(form.cleaned_data.get('book_start')) + ':00 to ' + str(form.cleaned_data.get('book_end')) + ':00 for Asset - ' + asset.title + ' on ' + bookingday + '.')
                    return redirect('/dashboard/' + owner + '/' + asset.title + '/bookingtable')

        else:
            messages.success(request, f'Form Invalid!')

    else:
        form = AssetBookForm(c=get_available_days_helper(asset))

    context = {
        'form': form,
        'title': 'Make Booking'
    }
    return render(request, 'table/asset_form.html', context)


# View to display Booking Table for an Asset
@login_required
def bookingtable(request, owner, asset):

    # From url arguments passed in, find corrosponding asset by owner and asset title
    assets = Asset.objects.all()
    for a in assets:
        if a.business_owner != None:
            if a.business_owner.username == owner and a.title == asset:
                asset = a

    # Call helper function to create Booking Table Matrix to be passed into Template
    bookings = booking_table_matrix_help(asset)

    context = {
        'bookings': bookings,
        'asset': asset,
    }

    return render(request, 'table/bookingtable.html', context)


# View for User to search for Businesses
@login_required
def SearchBusinesses(request):

    if request.method == 'POST':

        form = SearchBusinessesForm(request.POST)

        if form.is_valid():

            # Create context object for
            context = {'':''}
            context['businesses'] = User.objects.all()
            context['username'] = form.cleaned_data.get('username') # Business name User search for, form form
            context['assets'] = Asset.objects.all()

            return render(request, 'table/business_list.html', context)

        else:
            messages.warning(request, f'FORM IS INVALID')

    else:
        form = SearchBusinessesForm()

    return render(request, 'table/searchbusinesses.html', {'form': form})

# View to present Assets of a Business in a list, taking in argument owner as the Business owner
@login_required
def assetlist(request, owner):

    # Create context dict for template
    context = {'':''}
    context['assets'] = []

    # From all Asset objects find those owning to the 'owner'
    assets = Asset.objects.all()
    for a in assets:
        if a.business_owner != None:
            if a.business_owner.username == owner:
                context['assets'].append(a)

    return render(request, 'table/asset_list.html', context)


# View for Business to delete Asset
def delete_asset_view(request, owner, asset, pk):
    # Find profile for current logged in User
    profile = Profile.objects.filter(user=request.user)

    # If User is not signed up as Business, then redirect to Dashboard
    if (profile[0].userType != 'Business'):
        messages.warning(request,f'You are not a Business nor own this Booking Table')
        return redirect('/dashboard/' + owner + '/'  + asset + '/bookingtable')
    # If User is not owner of Asset
    elif profile[0].user.username != owner:
        messages.warning(request,f'You do not own this Booking Table')
        return redirect('/dashboard/' + owner + '/' + asset + '/bookingtable')

    asset_to_delete = Asset.objects.filter(id=pk)

    if request.method == 'POST':

        asset_to_delete.delete()
        messages.success(request, f'Sucesfully deleted Asset: ' + asset)
        return redirect('/dashboard/viewbookingtables/' + owner)

    else:

        return render(request, 'table/asset_delete.html')


# View for owner of Asset to delet it
def update_asset_view(request, owner, asset, pk):

    # Find profile for current logged in User
    profile = Profile.objects.filter(user=request.user)

    # If User is not signed up as Business, then redirect to Dashboard
    if (profile[0].userType != 'Business'):
        messages.warning(request, f'You are not a Business nor own this Booking Table')
        return redirect('/dashboard/' + owner + '/' + asset + '/bookingtable')
    # If User signed is not owner of Asset
    elif profile[0].user.username != owner:
        messages.warning(request, f'You do not own this Booking Table')
        return redirect('/dashboard/' + owner + '/' + asset + '/bookingtable')

    # If form is posted
    if request.method == 'POST':

        form = AssetUpdateForm(request.POST)

        if form.is_valid():

            # Find asset using pk, then update attributes and save
            asset = Asset.objects.filter(id=pk)[0]
            asset.title = form.cleaned_data['title']
            asset.description = form.cleaned_data['description']
            asset.location = form.cleaned_data['location']
            asset.save()

            return redirect('/dashboard/' + owner + '/' + asset.title + '/bookingtable')

        else:
            messages.success(request, f'Form Invalid!')

    else:
        form = AssetUpdateForm()

    context = {
        'form': form,
        'title': 'Update Booking Table'
    }

    return render(request, 'table/asset_form.html', context)


# View for user to delete booking
def delete_booking_view(request, pk):

    if request.method == 'POST':

        Booking.objects.filter(id=pk).delete()

        return redirect('/dashboard/viewbookings')

    else:

        return render(request, 'table/booking_delete.html')



# Help function to create booking table matrix
# If day is unavaible then will set table iteupdatedList as U for Unavailable
# If time slot is avaible then will set table item as A for Available
# If time slot is booked then will set table item as B for Booked
def booking_table_matrix_help(asset):

    bookings = [[]]
    bookings.remove([])

    # GET all booking objects for asset
    # filter by day
    # make booking string for each day

    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    day_bookings = []
    i = 0


    # For each day create list of bookings for that day, then add to list to iterate through
    for day in days:
        bookings1 = Booking.objects.filter(business_asset=asset, booking_day=day)
        list = ''


        for booking in bookings1:
            list += booking.booking_time + ':'

        list = list[:-1]
        day_bookings.append(list)

    # List of days available
    day_availability = [asset.mon_available, asset.tue_available, asset.wed_available, asset.thu_available, asset.fri_available,
                        asset.sat_available, asset.sun_available]

    # List of list of bookings for each day
    # day_bookings = [asset.tue_bookings, asset.wed_bookings, asset.thu_bookings, asset.fri_bookings,
    #                 asset.sat_bookings, asset.sun_bookings]

    # for first column (Monday) append approriate marker to matrix

    # mon_bookings = Booking.objects.filter(business_asset=asset, booking_day='Monday')

    # If asset not unavailable append U
    if not asset.mon_available:
        for t in range(asset.hour_start, asset.hour_end):
            bookings.append(['U'])

    # then (as asset available) if no bookings set every hour in first column monday as A available
    elif day_bookings[0] == '':
        for t in range(asset.hour_start, asset.hour_end):
            bookings.append(['A'])

    # then for every hour time slot check if there is booking on that time
    # and set approriate A or B booked
    else:
        booked = day_bookings[0].split(':')

        # for every hour in range of available hours
        for t in range(asset.hour_start, asset.hour_end):
            available = True
            # for every booking on this day
            for b in range(0, booked.__len__(), 2):
                # if booking is in the time of this hour, then set available to false
                if t >= int(booked[b]) and t < int(booked[b + 1]):
                    available = False

            # append A if no collision else B if there is booking for this time
            if available:
                bookings.append(['A'])
            else:
                bookings.append(['B'])

    i = 0

    # Now do the same for every day after Monday
    # Matrix format was created in previous for block
    # stored as bookings[hour][day] so that can table can be easily created in template, following MVC pattern

    for i in range(0,len(day_availability)):

        # Skip for monday
        if i == 0:
            continue;

        if not day_availability[i]:
            for t in range(asset.hour_start, asset.hour_end):
                bookings[t - asset.hour_start].append('U')
        elif day_bookings[i] == '':
            for t in range(asset.hour_start, asset.hour_end):
                bookings[t - asset.hour_start].append('A')

        else:
            booked = day_bookings[i].split(':')

            for t in range(asset.hour_start, asset.hour_end):
                available = True
                for b in range(0, booked.__len__(), 2):
                    if t >= int(booked[b]) and t < int(booked[b + 1]):
                        available = False

                if available:
                    bookings[t - asset.hour_start].append('A')
                else:
                    bookings[t - asset.hour_start].append('B')

        i += 1

    return bookings


# Helper function to get available day
def get_available_days_helper(asset):

    choices = []

    # If day is set as available then add to list
    if asset.mon_available:
        choices += [('Monday', "Monday")]
    if asset.tue_available:
        choices += [('Tuesday', "Tuesday")]
    if asset.wed_available:
        choices += [('Wednesday', "Wednesday")]
    if asset.thu_available:
        choices += [('Thursday', "Thursday")]
    if asset.fri_available:
        choices += [('Friday', "Friday")]
    if asset.sat_available:
        choices += [('Saturday', "Saturday")]
    if asset.sun_available:
        choices += [('Sunday', "Sunday")]

    return choices


def check_bookings_helper(asset, bookingtime, bookingday):

    day = ''

    bookings = Booking.objects.filter(business_asset=asset, booking_day=bookingday)
    list = ''
    for booking in bookings:
        list += booking.booking_time + ':'

    list = list[:-1]

    if list == '':
        return True

    bookinglist = list.split(':')
    st = int(bookingtime.split(':')[0])
    ft = int(bookingtime.split(':')[1])

    for t in range(0,len(bookinglist),2):
        if(st <= int(bookinglist[t]) and ft > int(bookinglist[t])) or (st < int(bookinglist[t + 1]) and ft >= int(bookinglist[t + 1])):
            return False

    return True


