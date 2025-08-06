from django import forms
from django.core.exceptions import ValidationError

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", forms.ClearableFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)

        return result

class FoodUploadForm(forms.Form):
    # images = forms.FileField(
    #     widget=forms.ClearableFileInput(attrs={
    #         "class": "form-control",
    #         "accept": "jpg,jpeg,png",
    #         "allow_multiple_selected": True
    #     }),
    #     required=False
    # )
    images = MultipleFileField(required=False)
    user_text = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "예: 나이 25세, 남성, 키 175cm, 몸무게 70kg, 평소 운동량 중간, 아침에 삶은 계란 2개 먹음....",
            "rows": 4
        }),
        required=False
    )

    def clean_images(self):
        images = self.files.getlist("images")

        if len(images) > 5: raise ValidationError("이미지는 한번에 최대 5개 까지만 업로드할 수 있습니다.")

        ALLOWED_EXT     = ["jpg", "jpeg", "png"]
        _5MB            = 5
        MAX_FILE_SIZE   = _5MB * 1024 * 1024         # 5MB

        wrong_types = []
        wrong_sizes = []
        for f in images:
            ext = f.name.split(".")[-1].lower()
            if ext not in ALLOWED_EXT:  wrong_types.append(f.name)
            if f.size > MAX_FILE_SIZE:  wrong_sizes.append(f.name)

        if wrong_types:  raise ValidationError(f"{", ".join(ALLOWED_EXT)} 파일만 업로드할 수 있습니다.<br/>{"<br/>".join(wrong_types)}")
        if wrong_sizes:  raise ValidationError(f"{_5MB}MB 를 넘는 파일은 업로드할 수 없습니다.<br/>{"<br/>".join(wrong_sizes)}")

        return images

    def clean(self):
        cleaned_data = super().clean()

        images = cleaned_data.get("images")
        text   = cleaned_data.get("user_text")

        if not images and not text:
            raise ValidationError("이미지나 텍스트 중 하나는 입력해주세요.")

        return cleaned_data