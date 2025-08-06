from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from .forms.chat_form import FoodUploadForm
from .include.inferer import *
from .include.util import *
from .models import MemberCreateForm


def intro(request):
    return render(request, "mainapp/intro.html")

def main(request):
    return render(request, "mainapp/main.html")

def chat(request):
    if request.method == "POST":
        form = FoodUploadForm(request.POST, request.FILES)
        if form.is_valid():
            images = [Image.open(img).convert('RGB') for img in form.cleaned_data["images"]]
            text   = form.cleaned_data["user_text"]

            context_info = {
                "image_info" : [],
                "user_text"  : text,
            }

            if request.user.is_authenticated:
                user = request.user.member
                context_info["user_info"] = f"키 {user.height}cm, 몸무게 {user.weight} kg, 나이 {user.age}"
                print("logged in user", context_info["user_info"])

            if images:
                inferer = OpenAIInferer("gpt-4o-mini")
                results = inferer(images)
                for _, food_dict in results.items():
                    menu_name   = food_dict["name"]
                    # ingredients = food_dict["ingredients"]
                    rag_context, calorie = get_menu_context_with_threshold(menu_name)
                    _image_info = {
                        "menu_name"   : menu_name,
                        "calorie"     : calorie,
                        "rag_context" : rag_context,
                    }
                    context_info["image_info"].append(_image_info)

            chat_history   = request.session.get("history", [])
            chat_history   = [tuple(item) for item in chat_history]
            final_response = analyze_meal_with_llm(context_info, chat_history)

            request.session["history"] = chat_history

            result_dict = {
                "user_text": f'{str(text)}',
                "answer"   : f"{str(final_response)}"
            }

            return JsonResponse(result_dict)
        else:
            print("\n\nERROR\n", form.errors)


    return render(request, "mainapp/chat.html", {"form":FoodUploadForm()})

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
    try:
        auth.logout(request)
    except Exception as e:
        print(e)

    return redirect( request.GET.get("next","mainapp:main"))

@login_required(login_url="/login")
def mypage(request):
    pass