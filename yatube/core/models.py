from django.db import models


class CreateModel(models.Model):
    """Abstract model adds create date"""
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        abstract = True
