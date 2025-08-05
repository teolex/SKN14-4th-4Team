from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Member(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday   = models.DateField (null=False, blank=False, default=date(2000, 1, 1))
    height     = models.FloatField(null=False, blank=False, default=160)
    weight     = models.FloatField(null=False, blank=False, default=50)
    picture    = models.ImageField(null=False, blank=False, upload_to='profile/')

    @property
    def age(self):
        today = date.today()
        birth = self.birthday
        return today.year - birth.year - ( (today.month, today.day) < (birth.month, birth.day) )


class MemberCreateForm(UserCreationForm):
    birthday   = forms.DateField (required=True, label="생일")
    height     = forms.FloatField(required=True, label="신장(cm)")
    weight     = forms.FloatField(required=True, label="무게(kg)")
    picture    = forms.ImageField(required=True, label="프로필")

    class Meta:
        model  = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]
        labels = ["아이디", "이름", "성", "이메일", "비밀번호", "비밀번호 확인"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i,field_nm in enumerate(self.Meta.fields):
            self.fields[field_nm].label = self.Meta.labels[i]

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def cleaned_member(self, params:dict):
        params = params or {}
        params["birthday"]  = self.cleaned_data["birthday"]
        params["height"]    = self.cleaned_data["height"]
        params["weight"]    = self.cleaned_data["weight"]
        params["picture"]   = self.cleaned_data["picture"]
        return Member(**params)

