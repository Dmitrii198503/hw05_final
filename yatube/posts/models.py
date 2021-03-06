from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreateModel


User = get_user_model()


class Group(models.Model):
    """Describes table which contains groups"""
    title = models.CharField(max_length=200, verbose_name='title')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='slug')
    description = models.TextField(verbose_name='description')

    class Meta:
        verbose_name = 'Group'

    def __str__(self) -> str:
        return self.title


class Post(CreateModel):
    """Describes table which contains posts"""
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите текст поста')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts', verbose_name='Автор')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name='posts',
                              verbose_name='Группа',
                              help_text='Выберите группу')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(CreateModel):
    """Describes comment to the post"""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Напишите комментарий'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text[:10]


class Follow(models.Model):
    """Describes signing up"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'Пдописчик: {self.user}, автор подписки {self.author}'
