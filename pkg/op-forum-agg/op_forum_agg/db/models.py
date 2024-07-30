from tortoise import fields
from tortoise.fields.relational import OneToOneFieldInstance
from tortoise.models import Model

import datetime
from typing import Any, Optional, Type, Union


def to_naive(value: datetime.datetime) -> datetime.datetime:
    if value.tzinfo is None:
        return value

    value = value.astimezone(datetime.timezone.utc)

    return value.replace(tzinfo=None)


class NaiveDatetimeField(fields.DatetimeField):
    skip_to_python_if_native = True

    class _db_postgres:  # noqa
        SQL_TYPE = "TIMESTAMP"

    def to_python_value(self, value: Any) -> Optional[datetime.datetime]:
        value = super().to_python_value(value)

        if value is None:
            return value

        return to_naive(value)

    def to_db_value(
        self,
        value: Optional[datetime.datetime],
        instance: "Union[Type[Model], Model]",
    ) -> Optional[datetime.datetime]:
        value = super().to_db_value(value, instance)

        if value is None:
            return value

        return to_naive(value)


class ForumPostCategory(Model):
    id = fields.IntField(pk=True)
    externalId = fields.CharField(max_length=255, unique=True)
    name = fields.CharField(max_length=255, null=True)
    color = fields.CharField(max_length=255, null=True)
    slug = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    topicUrl = fields.CharField(max_length=255, null=True)
    filterable = fields.BooleanField(default=False)

    forumPosts: fields.ReverseRelation["ForumPost"]

    class Meta:
        table = "ForumPostCategory"


class RawForumPost(Model):
    id = fields.IntField(pk=True)
    externalId = fields.CharField(max_length=255, unique=True)
    url = fields.CharField(max_length=255, unique=True)
    type = fields.CharField(max_length=255)
    rawData = fields.JSONField()

    forumPosts: fields.ReverseRelation["ForumPost"]

    class Meta:
        table = "RawForumPost"


class ForumPost(Model):
    id = fields.IntField(pk=True)
    externalId = fields.CharField(max_length=255, unique=True)
    url = fields.CharField(max_length=255, unique=True)
    title = fields.CharField(max_length=255)
    username = fields.CharField(max_length=255)
    displayUsername = fields.CharField(max_length=255)
    category = OneToOneFieldInstance(
        "models.ForumPostCategory",
        related_name="forumPosts",
        null=True,
        source_field="categoryId",
        to_field="id",
    )
    rawForumPost = OneToOneFieldInstance(
        "models.RawForumPost",
        related_name="forumPosts",
        null=True,
        source_field="rawForumPostId",
        to_field="id",
    )
    about = fields.TextField(null=True)
    firstPost = fields.TextField(null=True)
    reaction = fields.TextField(null=True)
    overview = fields.TextField(null=True)
    tldr = fields.TextField(null=True)
    classification = fields.CharField(max_length=255, null=True)
    readTime = fields.CharField(max_length=255, null=True)
    lastActivity = NaiveDatetimeField(null=True)
    createdAt = NaiveDatetimeField(auto_now_add=True)
    updatedAt = NaiveDatetimeField(auto_now=True)

    class Meta:
        table = "ForumPost"
