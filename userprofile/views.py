import hashlib
import os

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from my_blog import settings
from userprofile.forms import UserLoginForm, UserRegisterForm, ProfileForm
from userprofile.models import Profile


def user_login(request):
    """用户验证登录"""
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)  # 将提交的数据赋值给实例化form
        if user_login_form.is_valid():  # 判断数据是否符合模型要求，返回的是布尔值
            data = user_login_form.cleaned_data  # 清洗出合法数据，cleaned_data

            # 检验账号、密码是否正确匹配数据库中的某个用户
            # 如果均匹配则返回这个 user 对象
            # 只是验证一个用户的证书而已
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                login(request, user)  # 将用户数据保存在session中，即实现了登录动作
                return redirect('article:article_list')
            else:  # 如果user当中账号密码不正确
                return HttpResponse('账号或密码输入有误，请重新输入！')
        else:
            return HttpResponse('账号密码输入不符合要求')
    elif request.method == 'GET':  # 如果是GET
        user_login_form = UserLoginForm()  # 实例化表单类
        context = {
            'form': user_login_form,  # 给个表单让用户填写
        }
        return render(request, 'userprofile/login.html', context=context)  # 渲染出需要填写的表单
    else:
        return HttpResponse("请用GET或者POST请求")


def user_logout(request):
    """用户退出登录"""
    logout(request)
    return redirect('article:article_list')


def user_register(request):
    """用户注册"""
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)  # 将提交的数据表单数据赋值给新的变量
        if user_register_form.is_valid():  # 判断这些数据是否符合模型要求
            new_user = user_register_form.save(commit=False)  # 保存数据，但不保存到数据库
            new_user.set_password(user_register_form.cleaned_data['password'])  # 取出数据中的密码并设置成密码
            new_user.save()  # 保存到数据库
            login(request, new_user)  # 根据提供的账号密码登录重定向到首页
            return redirect('article:article_list')
        else:
            return HttpResponse('注册表单输入不符合要求，请重新输入！')  # 表单输入有误
    elif request.method == 'GET':  # 如果是get
        user_register_form = UserRegisterForm()  # 就将form生成的HTML表单渲染到注册页面当中
        context = {
            'form': user_register_form,
        }
        return render(request, 'userprofile/register.html', context=context)
    else:
        return HttpResponse('请使用POST或GET请求')


@login_required(login_url='/userprofile/login/')  # login_required装饰器：作用是需要验证登录才能删除，如果未登录就跳转登录路径login_url
def user_delete(request, id):
    """删除用户"""
    if request.method == 'POST':  # 提交登录表单，如果是POST
        user = User.objects.get(pk=id)  # 获取那个文章ID
        if request.user == user:  # POST提交的数据和数据库对比
            logout(request)  # 相同就退出登录
            user.delete()  # 删除用户
            return redirect('article:article_list')  # 并跳转到首页
        else:
            return HttpResponse('您没有删除权限！')
    else:
        return HttpResponse('仅接受POST请求！')


# 编辑用户信息
@login_required(login_url='/userprofile/login/')  # 首先做登录验证，以下是登录后才能执行
def profile_edit(request, id):
    user = User.objects.get(id=id)  # 根据ID获取用户所有信息
    # user_id 是 OneToOneField 自动生成的字段
    if Profile.objects.filter(user_id=id).exists():  # 判断是否为不为空
        # user_id 是 OneToOneField 自动生成的字段
        profile = Profile.objects.get(user_id=id)  # 如果不为空就获取user_id
    else:
        profile = Profile.objects.create(user=user)  # 如果为空就创建这个user

    if request.method == 'POST':  # 如果有提交数据
        if request.user != user:  # 验证修改数据者，是否为用户本人
            return HttpResponse("你没有权限修改此用户信息。")
        profile_form = ProfileForm(request.POST, request.FILES)  # 如果是本人，就将提交的数据生成formHTML表单并赋值
        if profile_form.is_valid():  # 是否合法
            # 取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data  # cleaned_data 读取表单返回的值
            profile.phone = profile_cd['phone']  # 取出phone对应值
            profile.bio = profile_cd['bio']  # 取出bIo对应值
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd['avatar']
                print('profile.avatar:', profile.avatar)
            profile.save()  # 保存到数据库
            return redirect("userprofile:edit", id=id)  # 跳转到edit页面,注意携带参数传递
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {
            'profile_form': profile_form,  # 未提交数据，就生成HTML表单
            'profile': profile,  # 未提交数据，就取出profile表中user_id对应的用户的phone,bio之类的信息
            'user': user,  # 为提交数据就取出user表中的所有内容
        }
        return render(request, 'userprofile/edit.html', context=context)
    else:
        return HttpResponse("请使用GET或POST请求数据")