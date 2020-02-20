from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from users.models import Profile
from table.models import Asset, Booking
from django.http import HttpResponse



class UserTests(TestCase):

    def test_user_created(self):
        client = Client()

        # Send post request to register html form, to register a Business user
        response = client.post(reverse('register'), {
            'username': 'testBusiness',
            'email': 'business@test.com',
            'password1': 'unsafe123',
            'password2': 'unsafe123',
            'userType': 'Business'
        }, secure=True)

        # Check Profile object was created correctly
        self.assertEquals(response.status_code, 302)
        newProfile = Profile.objects.all().last()
        self.assertEquals(newProfile.userType, 'Business')
        self.assertEquals(newProfile.user.username,'testBusiness')
        self.assertEquals(newProfile.user.email,'business@test.com')




        # Send post request to register html form, to register a User user
        response = client.post(reverse('register'), {
            'username': 'testUser',
            'email': 'user@test.com',
            'password1': 'unsafe123',
            'password2': 'unsafe123',
            'userType': 'User'
        }, secure=True)

        # Check Profile object was created correctly
        self.assertEquals(response.status_code, 302)
        newProfile = Profile.objects.all().last()
        self.assertEquals(newProfile.userType, 'User')
        self.assertEquals(newProfile.user.username, 'testUser')
        self.assertEquals(newProfile.user.email, 'user@test.com')




        # login to Business account
        response = client.post(reverse('login'), {
            'username': 'testBusiness',
            'password': 'unsafe123',
        }, secure=True)

        # check sign in
        self.assertEquals(response.status_code, 302)
        # check re-direct to dashboard
        self.assertTemplateUsed('table/dashboard.html')





        # update profile details
        response = client.post(reverse('profile'), {
            'username': 'testBusinessUpdated',
            'email': 'businessUpdated@test.com'
        }, secure=True)

        # check profile updated
        self.assertEquals(response.status_code, 302)
        updatedProfile = Profile.objects.all().first()
        self.assertEquals(updatedProfile.user.username, 'testBusinessUpdated')
        self.assertEquals(updatedProfile.user.email, 'businessUpdated@test.com')




        # create asset as signed in Business by posting data to asset create view
        response = client.post(reverse('table-asset_form'), {
            'title': 'businessAsset',
            'location': 'interweb',
            'description': 'Perfect Service',
            'hour_start': '0',
            'hour_end': '24',
            'mon_available': True,
            'tue_available': True,
            'wed_available': True,
            'thu_available': True,
            'fri_available': True,
            'sat_available': True,
            'sun_available': True
        }, secure=True)

        # check asset is created
        self.assertEquals(response.status_code, 302)
        asset = Asset.objects.all().last()
        self.assertEquals(asset.title, 'businessAsset')
        self.assertEquals(asset.location, 'interweb')
        self.assertEquals(asset.description, 'Perfect Service')
        self.assertEquals(asset.hour_start, 0)
        self.assertEquals(asset.hour_end, 24)





        # create another asset as signed in Business by posting data to asset create view
        response = client.post(reverse('table-asset_form'), {
            'title': 'businessAsset2',
            'location': 'interweb',
            'description': 'Perfect Service',
            'hour_start': '0',
            'hour_end': '24'
        }, secure=True)

        # check asset is created
        self.assertEquals(response.status_code, 302)
        asset = Asset.objects.all().last()
        self.assertEquals(asset.title, 'businessAsset2')
        self.assertEquals(asset.location, 'interweb')
        self.assertEquals(asset.description, 'Perfect Service')
        self.assertEquals(asset.hour_start, 0)
        self.assertEquals(asset.hour_end, 24)



        # Send post to edit asset
        response = client.post('/dashboard/testBusinessUpdated/businessAsset/update/2', data={
            'title': 'updatedTitle',
            'location': 'updatedLocation',
            'description': 'updatedDescription',
        }, secure=True)

        # Check asset edited
        a = Asset.objects.all().last()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(a.title, 'updatedTitle')
        self.assertEquals(a.location, 'updatedLocation')
        self.assertEquals(a.description, 'updatedDescription')



        # Send get request to view asset view
        response = client.get(reverse('table-viewbookingtables', kwargs={'owner': 'testBusinessUpdated'}), secure=True)

        # Check Assets in View Asset view
        self.assertEquals(response.status_code, 200)
        self.assertIn('updatedTitle', str(response.content))
        self.assertIn('updatedLocation', str(response.content))
        self.assertIn('updatedDescription', str(response.content))
        self.assertIn('businessAsset', str(response.content))
        self.assertIn('interweb', str(response.content))
        self.assertIn('Perfect Service', str(response.content))




        # post delete asset view
        response = client.post(reverse('table-asset_delete', kwargs={
            'owner': 'testBusinessUpdated',
            'asset': 'businessAsset2',
            'pk': 2
        }), secure=True)

        # check asset is deleted
        self.assertEquals(response.status_code, 302)
        asset = Asset.objects.all().last()
        self.assertNotEquals(asset.title, 'businessAsset2')



        # logout Business Account
        response = client.post(reverse('logout'), secure=True)
        # check log out
        self.assertEquals(response.status_code, 200)
        # check re-direct to logout page
        self.assertTemplateUsed('users/logout.html')



        # login to User account
        response = client.post(reverse('login'), {
            'username': 'testUser',
            'password': 'unsafe123',
        }, secure=True)

        # check sign in
        self.assertEquals(response.status_code, 302)
        # check re-direct to dashboard
        self.assertTemplateUsed('table/dashboard.html')




        # check search for Business
        response = client.post(reverse('table-searchbusinesses'), {
            'username': 'testBusiness'
        }, secure=True)

        # check return by checking html response contains business name and business's asset
        self.assertIn('testBusinessUpdated', str(response.content))
        self.assertIn('businessAsset', str(response.content))
        self.assertTemplateUsed('table/searchbusinesses.html')



        # check view booking table
        response = client.get(reverse('table-bookingtable', kwargs={
            'owner':'testBusinessUpdated',
            'asset':'businessAsset'
        }), secure=True)

        self.assertTemplateUsed('table/bookingtable.html')
        self.assertEquals(response.status_code, 200)



        # Send post to make booking
        response = client.post('/dashboard/testBusinessUpdated/businessAsset/makebooking', {
                    'choose_day': 'Monday',
                    'book_start': '5',
                    'book_end': '10',
        }, secure=True)

        # Check booking created
        b = Booking.objects.all().last()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(b.booking_time, '5:10')
        self.assertEquals(b.booking_day, 'Monday')



        # Send get request to view-bookings view
        response = client.get(reverse('table-viewbookings'), secure=True)

        # Check booking is listed
        self.assertEquals(response.status_code, 200)
        self.assertIn('5:10', str(response.content))
        self.assertIn('Monday', str(response.content))
        self.assertIn('testBusinessUpdated', str(response.content))


        # Send post request to delete booking view for this booking
        response = client.post(reverse('table-deletebooking', kwargs={'pk': 1}), secure=True)

        # Check booking delete
        b = Booking.objects.all().last()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(b, None)



