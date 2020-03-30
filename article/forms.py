from django import forms

from article.models import ArticlePost


# ModelForm 这个父类适合于需要直接与数据库交互的功能，比如新建、更新数据库的字段等,如果表单将用于直接添加或编辑Django模型，则可以使用 ModelForm来避免重复书写字段描述
class ArticlePostForm(forms.ModelForm):
    """定义一个form类"""
    class Meta:
        model = ArticlePost  # 指明数据模型来源
        fields = ('title', 'body')  # 定义表单包含的字段，也就是提交的内容
        # 在ArticlePost模型中，created和updated字段为自动生成，不需要填入；author字段暂时固定为id=1的管理员用户，
        # 也不用填入；剩下的title和body就是表单需要填入的内容了。
