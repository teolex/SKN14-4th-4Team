from pathlib import Path  # 파일 경로 조작성
from PIL import Image

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect

from .forms import SignUpForm, ChatForm, ProfileUpdateForm
from .models import UserProfile
from .inferer import OpenAIInferer
from .utils import (
    parse_prediction,
    get_menu_context_with_threshold,
    analyze_meal_with_llm
)
from .__init__ import vector_store

openai_inferer = OpenAIInferer()  # 이미지 식별 추론 (openai)                      


# 회원가입
def signup_view(request):
    # POST의 경우: request.POST
    if request.method == "POST":
        form = SignUpForm(request.POST)
        # 폼 유효성 검사
        if form.is_valid():
            # 사용자 객체 생성
            user = form.save()
            # UserProfile 객체 생성
            UserProfile.objects.create(
                user=user,
                height=form.cleaned_data['height'],
                weight=form.cleaned_data['weight'],
                age=form.cleaned_data['age'],
                gender=form.cleaned_data['gender'],
            )
            # 회원가입 후 로그인 처리 -> chat으로 리다이렉트
            login(request, user)
            return redirect('chat')
    # GET의 경우: 빈 폼 생성
    else:
        form = SignUpForm()
    # 폼을 context에 담아 render
    return render(request, "uauth/signup.html", {"form": form})

# 마이페이지 – 정보 조회
@login_required
def mypage(request):
    profile = request.user.userprofile
    return render(request, "app/mypage.html", {"profile": profile})

# 마이페이지 – 정보 수정
@login_required
def mypage_edit(request):
    profile = request.user.userprofile

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("mypage")
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, "app/mypage_edit.html", {"form": form})


# 홈
def home(request):
    return render(request, "app/home.html")


# 채팅
@login_required # 로그인하지 않은 사용자는 접근 불가
def chat(request):
    # 초기화 후 페이지 새로고침
    if request.method == "GET" and request.GET.get("reset") == "1":
        request.session.pop("chat_history", None)
        return redirect("chat")

    # 채팅이력, 텍스트, 에러메세지 초기화
    history = request.session.setdefault("chat_history", [])
    response = None
    images_error = None
    # 입력용 ChatForm 인스턴스 생성
    form = ChatForm()

    # POST 요청시 폼 데이터 새로 생성 & 파일 포함
    if request.method == "POST":
        form = ChatForm(request.POST, request.FILES)
        # print("FILES:", request.FILES)
        # print("POST:", request.POST)

        # 유효성 검사
        if form.is_valid():
            # 유저 메세지, 이미지 받기
            message = form.cleaned_data.get("message", "").strip()
            images = request.FILES.getlist("images")

            # 이미지 수 제한
            if len(images) > 5:
                images_error = "이미지는 최대 5장까지 업로드할 수 있습니다."
            else:
                for f in images:
                    if not f.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        images_error = f"{f.name}: jpg/png 파일만 가능합니다."
                        break
                    if f.size > 5 * 1024 * 1024:
                        images_error = f"{f.name}: 5MB 이하만 업로드할 수 있습니다."
                        break
            # 메세지, 이미지 둘 다 입력 안할시 에러메세지
            if not images and not message:
                images_error = "메시지나 이미지를 하나 이상 입력해 주세요."

            # 로그인 사용자 인적사항을 db에서 읽기
            profile = request.user.userprofile
            user_info = {
                "height": profile.height,
                "weight": profile.weight,
                "age": profile.age,
                "gender": profile.gender,
            }

            # 이미지를 하나씩 열고, openai 추론
            # 입력한 정보를 리스트에 저장
            menu_infos = []
            chat_images = []

            
            for f in images:
                # openai로 이미지 추론
                pil_img = Image.open(f).convert("RGB")
                pred = openai_inferer([pil_img], [f.name])[f.name]
                menu, _ = parse_prediction(pred)

                # pinecone 검색
                ctx, kcal = get_menu_context_with_threshold(vector_store, menu, k=3, threshold=0.4)

                # 이미지 임시 저장
                saved = _save_temp_image(f)
                chat_images.append(saved)

                menu_infos.append({
                    "filename": f.name,
                    "menu_name": menu,
                    "calorie": kcal,
                })

            # 텍스트만 입력된 경우
            if not images and message:
                menu_infos.append({
                    "filename": "-",
                    "menu_name": message,
                    "calorie": "",
                })

            # history에 사용자 입력을 추가
            if images or message:
                history.append((
                    "user",
                    message if message else "(이미지 전송)", chat_images
                ))

            # LLM 응답 생성
            try:
                if menu_infos:
                    response = analyze_meal_with_llm(
                        menu_infos=menu_infos,
                        user_info=user_info,
                        chat_history=history,
                    )
                    history.append(("assistant", response, None))
                else:
                    response = "이미지나 메시지를 입력해 주세요."
                    history.append(("assistant", response, None))
            except Exception as e:
                response = f"오류: {e}"
                history.append(("assistant", response, None))

            # 갱신된 대화를 세션 저장 후 POST-REDIRECT-GET 패턴으로 새로고침
            request.session["chat_history"] = history
            return redirect("chat")
        # 폼 에러시 에러메세지
        else:
            print("❌ form.errors:", form.errors)
    # GET 요청시 폼 생성
    else:
        form = ChatForm()
    # 템플릿 render
    ctx = {
        "form": form,
        "response": response,
        "chat_history": history,
        "images_error": images_error,
    }
    return render(request, "app/chat.html", ctx)


# 임시 이미지 저장 함수
def _save_temp_image(django_file):
    rel_path = f'chat_temp/{django_file.name}'
    temp_dir = Path(settings.MEDIA_ROOT) / "chat_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    filename = default_storage.save(rel_path, django_file)
    return default_storage.url(filename)
