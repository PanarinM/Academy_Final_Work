from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from users.forms import UserCreationForm, UserLoginForm, ProfileForm, PassChangeForm
from users.models import User


class Register(View):
    def get(self, request):
        next_ = request.GET.get('next') if request.GET.get('next') is not None else reverse('home')
        if request.user.is_authenticated:
            return HttpResponseRedirect(next_)
        return render(request, "register.html", {'creation_form': UserCreationForm, 'next': next_})

    def post(self, request):
        next_ = request.GET.get('next') if request.GET.get('next') is not None else reverse('home')
        if request.user.is_authenticated:
            return HttpResponseRedirect(next_)
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password2']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            avatar = form.cleaned_data["avatar"]
            user = User.objects.create_user(username, email, phone, password)
            if avatar is not None:
                user.avatar = avatar
                user.save()
            print(user.firstname, user.avatar.url)
            auth_user = authenticate(password=password, username=username)
            if auth_user:
                login(request, auth_user)
            return HttpResponseRedirect(next_)
        return render(request, "register.html", {'creation_form': form, 'next': next_})


class LogOut(View):
    def get(self, request):
        next_ = request.GET.get('next') if request.GET.get('next') is not None else reverse('home')
        if request.user.is_authenticated:
            logout(request)
        return HttpResponseRedirect(next_)


class LogIn(View):
    def get(self, request):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('home'))
        else:
            form = UserLoginForm()
            next_ = request.GET.get('next') if request.GET.get('next') is not None else reverse('home')
            return render(request, 'login.html', {'login_form': form, 'next': next_})

    def post(self, request):
        next_ = request.GET.get('next') if request.GET.get('next') is not None else reverse('home')
        if request.user.is_authenticated():
            return HttpResponseRedirect(next_)
        form = UserLoginForm(request.POST)
        if request.POST and form.is_valid():
            user = form.login(request)
            if user:
                login(request, user)
                return HttpResponseRedirect(next_)
        return render(request, 'login.html', {'login_form': form, 'next': next_})


class Profile(View):
    def get(self, request):
        if request.user.is_authenticated():
            user = request.user
            form = ProfileForm(instance=user)
            return render(request, 'profile.html', {'form': form})
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request):
        if request.user.is_authenticated():
            form = ProfileForm(request.POST)
            if form.is_valid():
                request.user.firstname = form.cleaned_data['firstname']
                request.user.lastname = form.cleaned_data['lastname']
                request.user.email = form.cleaned_data['email']
                request.user.phone = form.cleaned_data['phone']
                request.user.birthday = form.cleaned_data['birthday']
                request.user.avatar = form.cleaned_data['avatar']
                request.user.country = form.cleaned_data['country']
                request.user.city = form.cleaned_data['city']
                request.user.street = form.cleaned_data['street']
                request.user.house = form.cleaned_data['house']
                request.user.save()
                HttpResponseRedirect(reverse('home'))
            else:
                return render(request, 'profile.html', {'form': form})
        return HttpResponseRedirect(reverse('login'))


class PassChange(View):
    def get(self, request):
        if request.user.is_authenticated():
            form = PassChangeForm()
            return render(request, 'pass_change.html', {'form': form})
        else:
            return HttpResponseRedirect(reverse('login'))

    def post(self, request):
        if request.user.is_authenticated():
            form = PassChangeForm(request.POST)
            if form.is_valid():
                request.user.set_password(form.cleaned_data['password'])
                request.user.save()
                login(request, request.user)
                return HttpResponseRedirect(reverse('user_profile'))
            else:
                return render(request, 'pass_change.html', {'form': form})
        else:
            return HttpResponseRedirect(reverse('login'))
