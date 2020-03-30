import markdown
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from markdown import extensions

from article.forms import ArticlePostForm
from article.models import ArticlePost


def article_list(request):
    '''
    取出所有博客文章,返回的不再是所有文章的集合，
    而是对应页码的部分文章的对象，并且这个对象还包含了分页的方法
    '''
    search = request.GET.get('search')  # GET请求包含search字段
    order = request.GET.get('order')  # GET请求包含order字段
    if search:  # 如果search为True
        if order == 'total_views':  # 判断HTML form 表单传过来的是否是total_views
            # 用 Q对象 进行联合搜索，并且进行排序
            article_list = ArticlePost.objects.filter(  # 根据用户输入的search比较title和body进行筛选
                Q(title__icontains=search) |  # Q：实现逻辑判断，| 或，__icontains：忽略大小写
                Q(body__icontains=search)
            ).order_by('-total_views')  # 倒序排序，order_by:字段名称
        else:  # 如果没有点击最热文章，一样进行搜索比较，但是热点文章不会排序，就是最新排序
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
    else:  # 如果用户没有输入搜索内容，进行单纯的查看最热文章或最新文章
        # 将 search 参数重置为空
        search = ''  # 防止search为None报错
        if order == 'total_views':
            article_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            article_list = ArticlePost.objects.all()

    paginator = Paginator(article_list, 12)   # 将获取的所有文章分页，每页只能显示1篇文章
    page = request.GET.get('page')  # 获取url中的页面
    # print('request:', request)  #  '/article/article-list/?page=1' 获取的是个路径
    # print('request.GET:', request.GET)  #  <QueryDict: {'page': ['1']}>
    articles = paginator.get_page(page)  # 将导航对象相应的页码内容返回给 articles
    context = {
        'articles': articles,
        'order': order,  # 为什么把新变量order也传递到模板中？因为文章需要翻页！order给模板一个标识，提醒模板下一页应该如何排序
        'search': search,
    }
    # render函数：载入模板，并返回context对象
    return render(request, 'article/list.html', context=context)


def article_detail(request, id):
    """文章详情页面"""
    article = ArticlePost.objects.get(pk=id)
    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])  # update_fields=[]指定了数据库只更新total_views字段，优化执行效率。

    # 将正文Body转换成markdown格式，两个参数
    # article.body = markdown.markdown(
    #     article.body,  # 第一个参数是文章正文
    #     extensions=[  # 第二个参数是markdown扩展设置
    #         'markdown.extensions.extra',  # 包含 缩写、表格等常用扩展
    #         'markdown.extensions.codehilite',   # 语法高亮扩展
    #
    #         # 目录扩展
    #         'markdown.extensions.toc',
    #     ]
    # )
    # context = {
    #     'article': article,
    # }

    # 修改 Markdown 语法渲染
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)

    # 新增了md.toc对象
    context = {'article': article, 'toc': md.toc}
    return render(request, 'article/detail.html', context=context)


@login_required(login_url='/userprofile/login/')
def article_create(request):
    """提交表单数据的处理"""
    if request.method == "POST":  # 如果接受到提交数据
        article_post_form = ArticlePostForm(data=request.POST)  # 如果是提交了数据就将提交数据赋值给表单实例中
        if article_post_form.is_valid():  # 判断数据是否符合模型要求
            new_article = article_post_form.save(commit=False)  # 保存提交的数据，暂不提交到数据库
            new_article.author = User.objects.get(id=request.user.id)  # 传入id为1的用户
            # 以上做了操作：首先是将提交的内容赋值给form表单的实例化，然后判断它是不是符合要求，
            # 然后保存将数据暂时保存到内存中，不保存到数据库，最后是把作者也传给他，那么现在数据就是标题，内容，作者

            new_article.save()  # 保存到数据库
            return redirect('article:article_list')  # 最后重定向到首页
        else:
            return HttpResponse('表单内容有误，请重新填写')
    else:  # 如果没有接受到提交的数据，就渲染页面填写
        article_post_form = ArticlePostForm()
        context = {
            'article_post_form': article_post_form,
        }
        return render(request, 'article/create.html', context=context)


# @login_required(login_url='/userprofile/login/')
# def article_delete(request, id):
#     """文章删除"""
#     article = ArticlePost.objects.get(pk=id)
#     article.delete()
#     return redirect('article:article_list')


@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    """安全删除文章"""
    article = ArticlePost.objects.get(pk=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权删除这篇文章。")
    if request.method == "POST":
        article = ArticlePost.objects.get(pk=id)
        article.delete()
        return redirect('article:article_list')
    else:
        return HttpResponse('仅允许post请求')


@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """更新文章"""
    # 同post方法提交表单，更新的字段有 title、body
    article = ArticlePost.objects.get(pk=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    if request.method == 'POST':  # 如果有post过来数据
        article_post_form = ArticlePostForm(data=request.POST)  # 如果是post就将提交的数据赋值到实例表单中
        if article_post_form.is_valid():  # 判断提交数据符合模型要求
            article.title = request.POST['title']  # 将新数据覆盖原来的数据，title
            article.body = request.POST['body']
            article.save()  # 保存数据库
            return redirect('article:article_detail', id=id)  # 修改成功后跳转到文章详情页面
        else:  # 如果提交数据不合法就给提示
            return HttpResponse("表单内容有误，请重新填写")
    else:  # 用Get方法 获取旧数据
        article_post_form = ArticlePostForm()  # 创建实例化表单
        context = {
            'article': article,
            'article_post_form': article_post_form,
        }
        return render(request, 'article/update.html', context=context)