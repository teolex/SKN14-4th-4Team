from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

# 회원가입 클래스  - UserCreationForm으로 비밀번호 기능                                  
class SignUpForm(UserCreationForm):
    # 사용자 신체 정보
    height = forms.FloatField(
        label="키(cm)",
        validators=[MinValueValidator(100), MaxValueValidator(250)],
        widget=forms.NumberInput(attrs={"min": "100", "max": "250", "step": "0.1"}),
    )
    weight = forms.FloatField(
        label="몸무게(kg)",
        validators=[MinValueValidator(30), MaxValueValidator(250)],
        widget=forms.NumberInput(attrs={"min": "0", "max": "150", "step": "0.1"}),
    )
    age = forms.FloatField(
        label="나이",
        validators=[MinValueValidator(10), MaxValueValidator(120)],
        widget=forms.NumberInput(attrs={"min": "1", "max": "120", "step": "1"}),
    )
    gender = forms.ChoiceField(
        label="성별", choices=(("M", "남"), ("F", "여")), required=True
    )

    # User & 폼에 포함할 필드 지정
    class Meta:
        model = User
        fields = ("username", "password1", "password2", "height", "weight", "age", "gender")

# 프로필 수정
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = UserProfile
        fields = ["height", "weight", "age", "gender"]
        widgets = {
            "height": forms.NumberInput(attrs={"class": "form-control", "min": 100, "max": 250, "step": 0.1}),
            "weight": forms.NumberInput(attrs={"class": "form-control", "min": 30,  "max": 250, "step": 0.1}),
            "age":    forms.NumberInput(attrs={"class": "form-control", "min": 10,  "max": 120, "step": 1}),
            "gender": forms.Select(attrs={"class": "form-select"}),
        }

# 이미지 파일명 확장자 검사용 함수
def _img_ok(name: str):
    return name.strip().lower().endswith((".jpg", ".jpeg", ".png"))

# 채팅 (텍스트, 이미지 업로드)
class ChatForm(forms.Form):
    message = forms.CharField(
        label="메시지",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
    )

    images = forms.FileField(
        label="음식 이미지 (최대 5장)",
        required=False,
        widget=forms.ClearableFileInput(),
        help_text="jpg / png 파일을 최대 5장까지 업로드할 수 있습니다.",
    )



