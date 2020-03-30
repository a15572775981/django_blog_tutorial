from django import forms


# forms.Form则需要手动配置每个字段，它适用于不与数据库进行直接交互的功能。用户登录不需要对数据库进行任何改动，因此直接继承forms.Form就可以了
from django.contrib.auth.models import User

from userprofile.models import Profile


class UserLoginForm(forms.Form):
    """登录表单"""
    username = forms.CharField()
    password = forms.CharField()


class UserRegisterForm(forms.ModelForm):
    """注册表单"""
    password = forms.CharField()
    password2 = forms.CharField()  # 密码两次输入

    class Meta:
        model = User
        fields = ('username', 'email')  # 覆写某字段之后，内部类class Meta中的定义对这个字段就没有效果了，所以fields不用包含password

    def clean_password2(self):  # def clean_[字段]这种写法Django会自动调用，来对单个字段的数据进行验证清洗。
        """登录密码校验"""
        data = self.cleaned_data  # cleaned_data：提交表单的返回值
        if data.get('password') == data.get('password2'):  # 比较两次输入如果一致，取出第一次输入的密码
            return data.get('password')
        else:
            raise forms.ValidationError('密码输入不一致，请再次输入')


class ProfileForm(forms.ModelForm):
    """新建一个表单类"""
    class Meta:
        model = Profile
        fields = ('phone', 'avatar', 'bio')