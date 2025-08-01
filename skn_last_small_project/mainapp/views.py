from django.shortcuts import render, redirect
from django.contrib import auth
from .models import MemberCreateForm, Member


# Create your views here.

def intro(request):
    return render(request, "mainapp/intro.html")

def main(request):
    return render(request, "mainapp/main.html")

def chat(request):
    return render(request, "mainapp/chat.html")



def signup(request):
    if request.method == "POST":
        form = MemberCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user   = form.save()
            member = form.cleaned_member({"user":user})
            member.save()

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            authed_user =auth.authenticate(username=username, password=password)
            if authed_user is not None:
                auth.login(request, authed_user)
                return redirect("mainapp:main")
            else:
                return redirect("mainapp:login")
    else:
        form = MemberCreateForm()

    return render(request, "mainapp/signup.html", {"form": form})

def logout(request):
    auth.logout(request)
    return redirect("mainapp:main")