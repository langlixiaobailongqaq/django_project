from django.db import models
from django.contrib.auth.models import User
# django-mptt
from mptt.models import MPTTModel, TreeForeignKey
from article.models import ArticlePost
from ckeditor.fields import RichTextField


# 博文的评论
class Comment(MPTTModel):
    # 被评论的文章
    article = models.ForeignKey(ArticlePost, on_delete=models.CASCADE, related_name='comments', verbose_name='被评论的文章')
    # 评论的发布者
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment', verbose_name='评论的发布者')
    # body = models.TextField()
    # RichTextField: django-ckeditor库自己的富文本字段
    body = RichTextField()
    created = models.DateTimeField(auto_now_add=True)
    # mptt 树形结构
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    # 记录二级评论回复给谁，str
    reply_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='replyers')

    # class Meta:
    #     ordering = ('created',)
    class MPTTMeta:
        order_insertion_by = ['created']

    def __str__(self):
        return self.body[:20]
