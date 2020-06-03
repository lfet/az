from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ChooseProfileTypeForm
from django.contrib.auth.models import User
from .models import Profile

# View to register new user
def register(request):

    if request.method == 'POST':

        # form for User and Profile models
        r_form = UserRegisterForm(request.POST)
        c_form = ChooseProfileTypeForm(request.POST)

        if r_form.is_valid():
            r_form.save()

            # # If Profile type is Business, then set default display picture accordingly
            if request.POST.copy().get('userType') == 'Business':
                print(request.POST.copy().get('userType'))
                # Create Profile object along with User,
                # more efficient than using Signals as form entry can be directly inserted for choose default display image
                Profile.objects.create(user=User.objects.all().last(), userType=request.POST.copy().get('userType'), image='default-business.jpg')
            else:
                Profile.objects.create(user=User.objects.all().last(), userType=request.POST.copy().get('userType'))

            username = r_form.cleaned_data.get('username')
            messages.success(request,f'Account crated for {username}!')

            return redirect('login')

        else:
            messages.success(request, f'Form Invalid!')

    else:
        r_form = UserRegisterForm()
        c_form = ChooseProfileTypeForm()

    return render(request,'users/register.html', {'r_form': r_form, 'c_form': c_form})

# View for Profile
@login_required
def profile(request):
    if request.method == 'POST':

        # Update forms for User and Profile Model
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
        else:
            messages.success(request, f'Form Invalid!')


    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)