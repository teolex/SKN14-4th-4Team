from django.conf import settings
from django.contrib import auth
from django.http import JsonResponse
from django.shortcuts import render, redirect
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from .forms.chat_form import FoodUploadForm
from .include.inferer import *
from .include.util import *
from .models import MemberCreateForm


# Create your views here.

# pc           = Pinecone(pinecone_api_key=settings.PINECONE_PJ_KEY)
# index        = pc.Index(settings.INDEX_NAME)
# embeddings   = OpenAIEmbeddings(model=settings.EMBED_MODEL)
# vector_store = PineconeVectorStore(index=index, embedding=embeddings)

def intro(request):
    return render(request, "mainapp/intro.html")

def main(request):
    return render(request, "mainapp/main.html")

def chat(request):
    if request.method == "POST":
        form = FoodUploadForm(request.POST, request.FILES)
        if form.is_valid():
            images = [Inferer.to_pil_image(img) for img in form.cleaned_data["images"]]
            names  = [f.name for f in form.cleaned_data["images"]]
            text   = form.cleaned_data["user_text"]

            pc           = Pinecone(api_key=settings.PINECONE_PJ_KEY)
            index        = pc.Index(settings.INDEX_NAME)
            embeddings   = OpenAIEmbeddings(model=settings.EMBED_MODEL)
            vector_store = PineconeVectorStore(index=index, embedding=embeddings)

            menu_infos  = []

            if images and not text:
                inferer = OpenAIInferer("gpt-4o-mini")
                results = inferer(images, names)
                for filename, pred_str in results.items():
                    menu_name, ingredients = parse_prediction(pred_str)
                    rag_context, calorie = get_menu_context_with_threshold(vector_store, menu_name)
                    menu_infos.append({
                        "filename": filename,
                        "menu_name": menu_name,
                        "calorie": calorie,
                        "ingredients": ingredients,
                        "rag_context": rag_context
                    })
            elif not images and text:
                menu_infos.append({
                    "filename": "-",
                    "menu_name": text,
                    "calorie": "",
                    "ingredients": "",
                    "rag_context": ""
                })

            chat_history = request.session.get("history", [])
            print(f"last 2 chat_history = {chat_history[-2:]}")

            # 최종 분석 (이미지, 텍스트 모두 menu_infos에 들어감)
            final_response = analyze_meal_with_llm(
                menu_infos=menu_infos,
                user_info=text,
                chat_history=chat_history
            )
            chat_history.append(("user", text, images))
            chat_history.append(("assistant", final_response, None))
            request.session["history"] = chat_history

            return JsonResponse({
                "user_text" : f'{text}',
                "answer"    : f"{final_response}"
            })
        else:
            print("\n\nERROR\n", form.errors)
    else:
        form = FoodUploadForm()

    return render(request, "mainapp/chat.html", {"form":form})

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
    return redirect( request.GET.get("next","mainapp:main"))