from django import forms
from django.contrib.auth.models import User
import re
class Register_form(forms.Form):

    username = forms.CharField(
        max_length=20,
        min_length=6,
        label="用户名",
        error_messages={
            'required':"不能为空!",
            'min_length':"用户名太短!",
        }
    )

    password = forms.CharField(
        label="密码",
        max_length=20,
        min_length=6,
        widget=forms.widgets.PasswordInput(render_value=True)
    )

    password2 = forms.CharField(
        label="确认密码",
        max_length=20,
        min_length=6,
        widget=forms.widgets.PasswordInput(render_value=True)
    )

    email = forms.EmailField(
        max_length=20,
        min_length=6,
        label="邮箱",  
        error_messages={
            "required":"不能为空!",
            "invalid":"请输入一个有效的邮箱地址!",
        }
    )

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class":"form-control"})

    def clean_username(self):
        username = self.cleaned_data.get("username")
        ret = re.search(r'^[0-9A-Za-z]{6,20}$',username)
        if ret:
            if User.objects.filter(username=username):
                self.add_error("username", "该用户名已经存在.")
            else:
                return username
        else:
            self.add_error("username","用户名不符合规则,规则:字母数字组成6-20位.")

    def clean_password2(self):
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("password2")
        if p1 == p2:
            return p2
        else:
            self.add_error("password2","两次密码不一致！")