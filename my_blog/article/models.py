from django.db import models
# 导入内建的User 模型
from django.contrib.auth.models import User
# timezone 用于处理时间相关事务
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from PIL import Image


class ArticleColumn(models.Model):
    """
    栏目的 Model
    """
    # 栏目标题
    title = models.CharField(max_length=100, blank=True, verbose_name='栏目标题')
    # 创建时间
    created = models.DateTimeField(default=timezone.now, verbose_name='创建时间')

    def __str__(self):
        return self.title


# 博客文章数据模型
class ArticlePost(models.Model):
    # 文章作者。参数 on_delete 用于指定数据删除的方式
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='文章作者')
    # 文章标题。 models.CharField 为字符串字段，用于保存较短的字符串，比如标题
    title = models.CharField(max_length=100, verbose_name='文章标题')
    # 文章正文。保存大量文本使用 TextField
    body = models.TextField(verbose_name='文章正文')
    # 文章浏览量-PositiveIntegerField：用于存储正整数
    total_views = models.PositiveIntegerField(default=0, verbose_name='文章浏览量')
    # 文章创建时间。参数 default=timezone.now 指定其在创建数据时将默认写入当前的时间
    created = models.DateTimeField(default=timezone.now, verbose_name='文章创建时间')
    # 文章更新时间。参数 auto_now=True 指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True, verbose_name='文章更新时间')
    # 文章栏目的 一对多 外键
    column = models.ForeignKey(ArticleColumn, null=True, blank=True, on_delete=models.CASCADE, related_name='article'
                               ,verbose_name='文章栏目')
    # 文章标签
    tags = TaggableManager(blank=True, verbose_name='文章标签')
    # 文章标题图
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True, verbose_name='文章标题图')
    # 点赞数统计
    likes = models.PositiveIntegerField(default=0)

    # 保存时处理图片
    def save(self, *args, **kwargs):
        # 调用原有的 save() 的功能
        article = super(ArticlePost, self).save(*args, **kwargs)
        # 固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y/x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)
        return article

    # 内部类 class Meta 用于 model 定义元数据
    class Meta:
        # ordering 指定模型返回的数据的排列顺序
        # '-created' 表明数据应该以倒pt序排列
        ordering = ('-created',)

    # 函数 __str__ 定义当调用对象的 str()方法时的返回值内容
    def __str__(self):
        # return self.title 将文章标题返回
        return self.title

    # 获取文章的地址
    def get_absolute_url(self):
        # 通过reverse()方法返回文章详情页面的url，实现了路由重定向。
        return reverse('article:article_detail', args=[self.id])

    def was_created_recently(self):
        """ 若文章是‘最近’发表的，则返回 True """
        diff = timezone.now() - self.created
        # if diff.days <= 0 and diff.seconds < 60:
        if diff.days == 0 and diff.days >= 0 and diff.seconds < 60:
            return True
        else:
            return False
