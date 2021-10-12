from django.contrib import admin
# 导入 ArticlePost
from .models import ArticlePost, ArticleColumn

# Register your models here.


# 注册 ArticlePost 到 admin 中
admin.site.register(ArticlePost)
# 注册 文章栏目
admin.site.register(ArticleColumn)
