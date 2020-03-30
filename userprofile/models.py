from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    # 与 User 模型构成一对一的关系
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # 电话号码字段
    phone = models.CharField(max_length=20, blank=True)
    # 头像， /%Y%m%d/ 以时间格式化来设置路径文件夹
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)  # upload_to ： 文件上传后将自动保存到项目根目录的media文件夹中
    # 个人简介
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return 'user {}'.format(self.user.username)

    objects = models.Manager()
