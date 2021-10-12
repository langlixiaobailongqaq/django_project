from django.test import TestCase
import datetime
from django.utils import timezone
from django.urls import reverse
from time import sleep
from article.models import ArticlePost
from django.contrib.auth.models import User


class ArticlePostModelTest(TestCase):
    """
    首先测试系统会在所有以tests开头的文件中寻找测试代码
        所有TestCase的子类都被认为是测试代码
        系统创建了一个特殊的数据库供测试使用，即所有测试产生的数据不会对你自己的数据库造成影响
        类中所有以test开头的方法会被认为是测试用例
        在运行测试用例时，assertIs抛出异常，因为True is not False
        完成测试后，自动销毁测试数据库
    运行自动化测试：python manage.py test
    """

    def test_was_created_recently_with_future_article(self):
        # 若文章创建时间为未来，返回false
        author = User(username='user', password='test_password')
        author.save()

        future_article = ArticlePost(
            author=author,
            title='test',
            body='test',
            created=timezone.now() + datetime.timedelta(days=30)
        )
        # 断言
        self.assertIs(future_article.was_created_recently(), False)

    def test_was_created_recently_with_seconds_before_article(self):
        """ 若文章创建时间为1分钟内，则返回True """
        author = User(username='user1', password='test_password')
        author.save()
        seconds_before_article = ArticlePost(
            author=author,
            title='test1',
            body='test1',
            created=timezone.now() - datetime.timedelta(seconds=45)
        )
        self.assertIs(seconds_before_article.was_created_recently(), True)

    def test_was_created_recently_with_hours_before_article(self):
        # 若文章创建时间为几小时前，返回 False
        author = User(username='user2', password='test_password')
        author.save()
        hours_before_article = ArticlePost(
            author=author,
            title='test2',
            body='test2',
            created=timezone.now() - datetime.timedelta(hours=3)
        )
        self.assertIs(hours_before_article.was_created_recently(), False)

    def test_was_created_recently_with_days_before_article(self):
        # 若文章创建时间为几天前，返回 False
        author = User(username='user3', password='test_password')
        author.save()
        months_before_article = ArticlePost(
            author=author,
            title='test3',
            body='test3',
            created=timezone.now() - datetime.timedelta(days=5)
        )
        self.assertIs(months_before_article.was_created_recently(), False)

    def test_increase_views(self):
        # 请求详情试图时，阅读量 +1
        author = User(username='user4', password='test_password')
        author.save()
        article = ArticlePost(
            author=author,
            title='test4',
            body='test4',
        )
        article.save()
        self.assertIs(article.total_views, 0)

        url = reverse('article:article_detail', args=(article.id,))
        response = self.client.get(url)
        viewed_article = ArticlePost.objects.get(id=article.id)
        self.assertIs(viewed_article.total_views, 1)

    def test_increase_views_but_not_change_updated_field(self):
        # 请求详情视图时，不改变 updated 字段
        author = User(username='user5', password='test_password')
        author.save()
        article = ArticlePost(
            author=author,
            title='test5',
            body='test5',
        )
        article.save()
        sleep(0.5)
        url = reverse('article:article_detail', args=(article.id,))
        response = self.client.get(url)
        viewed_article = ArticlePost.objects.get(id=article.id)
        self.assertIs(viewed_article.updated - viewed_article.created < timezone.timedelta(seconds=0.1), True)