from django.conf.urls import url

from users.views import Register, LogOut, LogIn, Profile, PassChange

urlpatterns = [
    url(r'^register/$', Register.as_view(), name="register"),
    url(r'^logout/$', LogOut.as_view(), name="logout"),
    url(r'^login/$', LogIn.as_view(), name="login"),
    url(r'^profile/$', Profile.as_view(), name="user_profile"),
    url(r'^profile/passchange$', PassChange.as_view(), name="pass_change"),
]