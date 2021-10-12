# 导入 HttpResponse 模块
from django.http import HttpResponse
# 导入 redirect 重定向模块
from django.shortcuts import render, redirect
# 引入 User模型
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# 引入分页模块
from django.core.paginator import Paginator
# 引入 Q 对象
from django.db.models import Q
from django.views import View
# 引入 markdown 模块
import markdown
from my_blog.settings import LOGGING
import logging
# 导入数据模型 ArticlePost
from article.models import ArticlePost, ArticleColumn
from article.forms import ArticlePostForm
from comment.models import Comment
from comment.forms import CommentForm

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('django.request')


# 视图函数-博客列表
def article_list(request):
    # 从 url中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    # 初始化查询集
    article_list = ArticlePost.objects.all()

    # 搜索查询集
    if search:
        article_list = article_list.filter(Q(title__icontains=search) | Q(body__icontains=search))
    else:
        # 将 search 参数重置为空
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    # # 根据GET请求中查询条件, 返回不同排序的对象数组
    # if request.GET.get('order') == 'total_views':
    #     articles_list = ArticlePost.objects.all().order_by('-total_views')
    #     order = 'total_views'
    # else:
    #     articles_list = ArticlePost.objects.all()
    #     order = 'total_views'

    # 每页显示1篇文章
    paginator = Paginator(article_list, 3)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)
    # 需要传递给模板（templates）的对象
    context = {'articles': articles, 'order': order, 'search': search, 'column': column, 'tag': tag}
    return render(request, 'article/list.html', context)


# 文章详情
def article_detail(request, id):
    # 取出相应的文章
    article = ArticlePost.objects.get(id=id)
    # 取出文章评论
    comments = Comment.objects.filter(article=id)
    # 判断作者修改和阅读不增加阅读量
    if request.user != article.author:
        # 浏览量 +1
        article.total_views += 1
        # update_fields=[] 指定数据库只更新total_views字段，优化执行效率
        article.save(update_fields=['total_views'])
    # 将 markdown 语法渲染成 html样式
    md = markdown.Markdown(
        extensions=[
            # 包含 缩写、表格等常用扩展
            'markdown.extensions.extra',
            # 语法高亮扩展
            'markdown.extensions.codehilite',
            # 目录扩展
            'markdown.extensions.toc',
        ])
    # convert()方法将正文渲染为html页面
    article.body = md.convert(article.body)
    # 引入评论表单
    comment_form = CommentForm()

    # 过滤出所有的id比当前文章小的文章
    pre_article = ArticlePost.objects.filter(id__lt=article.id).order_by('-id')
    # 过滤出id大的文章
    next_article = ArticlePost.objects.filter(id__gt=article.id).order_by('id')
    # 取出相邻前一篇的文章
    if pre_article.count() > 0:
        pre_article = pre_article[0]
    else:
        pre_article = None
    # 取出相邻后的一篇文章
    if next_article.count() > 0:
        next_article = next_article[0]
    else:
        next_article = None

    # 需要传递给模板的对象
    context = {
        'article': article,
        'toc': md.toc,
        'comments': comments,
        'comment_form': comment_form,
        'pre_article': pre_article,
        'next_article': next_article,
    }
    logger.info("文章详情")
    # 载入模板，并返回context 对象
    return render(request, 'article/detail.html', context)


# 写文章的视图
# 检查登录
@login_required(login_url='/userprofile/login')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == 'POST':
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1 的用户
            # 指定目前登录的用户为作者
            new_article.author = User.objects.get(id=request.user.id)
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 将新文章保存到数据库中
            new_article.save()
            # 保存 tags的多对多关系
            article_post_form.save_m2m()
            # 完成后返回文章列表
            logger.info('完成后返回文章列表')
            return redirect('article:article_list')
        # 如果数据不合法，返回错误信息
        else:
            logger.warning('表单内容有误')
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单实例
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = {'article_post_form': article_post_form, 'columns': columns}
        # 返回模板
        return render(request, 'article/create.html', context)


# 删文章(弃用)
def article_delete(request, id):
    # 根据 id 获取需要删除的文章
    article = ArticlePost.objects.get(id=id)
    # 调用 .delete() 方法删除文章
    article.delete()
    # 完成删除后返回文章列表
    return redirect('article:article_list')


# 安全删除文章
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")


# -- 更新文章 --
# 提醒用户登录
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST 方法提交表单，更新title、body字段
    GET 方法进入初始表单页面
    id：文章的 id
    """
    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章！")
    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')
                article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:article_detail", id=id)
        else:
            # 如果数据不合法，返回错误信息
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的的内容
        context = {'article': article, 'article_post_form': article_post_form,
                   'tags': ','.join([x for x in article.tags.names()])}
        # 将响应返回到模板中
        return render(request, 'article/update.html', context)


# 点赞数+1
class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')