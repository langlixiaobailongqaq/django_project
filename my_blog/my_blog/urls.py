"""my_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# 引入 include
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from article.views import article_list


# 存放映射关系的列表
urlpatterns = [
    # 首页 http://127.0.0.1:8000/accounts/login/
    path('', article_list, name='home'),
    path('admin/', admin.site.urls),
    # 配置 app 的url, namespace可以保证反查到唯一的url
    path('article/', include('article.urls', namespace='article')),
    path('userprofile/', include('userprofile.urls', namespace='userprofile')),
    path('password_reset/', include('password_reset.urls')),
    # 评论
    path('comment/', include('comment.urls', namespace='comment')),
    # 消息通知
    path('inbox/notifications', include('notifications.urls', namespace='notifications')),
    # notice
    path('notice/', include('notice.urls', namespace='notice')),
    # django-allauth
    path('accounts/', include('allauth.urls')),
]

# 上传图片路径
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)