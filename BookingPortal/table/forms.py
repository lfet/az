from django import forms
from django.contrib.auth.models import User
from .models import Asset


# Creation Form for Business to create Asset
class AssetCreateForm(forms.ModelForm):
    hour_start = forms.IntegerField(label='Start Hour - 24 Hour Time (0 - 23)',min_value=0, max_value=24)
    hour_end = forms.IntegerField(label='End Hour 24 Hour Time (1 - 24)', min_value=0, max_value=24)

    class Meta:
        model = Asset
        fields = ['title','location', 'description','hour_start','hour_end','mon_available','tue_available','wed_available','thu_available','fri_available','sat_available','sun_available']


# Booking Form for User to book Business's Asset
class AssetBookForm(forms.ModelForm):

    # Overwrite for init method,
    # needed to dynamically display choices for 'day' field
    # so that user can only select from available days
    def __init__(self, *args, **kwargs):
        c = kwargs.pop('c')
        super(AssetBookForm, self).__init__(*args, **kwargs)
        self.fields['choose_day'] = forms.ChoiceField(choices=c, label="Select Day")

    choose_day = forms.ChoiceField()
    book_start = forms.IntegerField(label='Start Hour - 24 Hour Time (0 - 23)', min_value=0, max_value=24)
    book_end = forms.IntegerField(label='End Hour 24 Hour Time (1 - 24)', min_value=0, max_value=24)

    class Meta:
        model = Asset
        fields = ['choose_day','book_start','book_end']


class SearchBusinessesForm(forms.Form):
    username = forms.CharField(label='Business Name')


class AssetUpdateForm(forms.ModelForm):

    class Meta:
        model = Asset
        fields = ['title', 'location','description']
