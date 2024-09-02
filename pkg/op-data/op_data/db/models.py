from tortoise import fields
from tortoise.fields.relational import OneToOneFieldInstance
from tortoise.models import Model

import datetime
from typing import Any, Optional, Type, Union


def to_naive(value: datetime.datetime) -> datetime.datetime:
    """Convert a datetime to naive UTC."""
    if value.tzinfo is None:
        return value

    return value.astimezone(datetime.timezone.utc).replace(tzinfo=None)


class NaiveDatetimeField(fields.DatetimeField):
    """A DatetimeField that stores datetimes in naive UTC format."""

    skip_to_python_if_native = True

    class _db_postgres:  # noqa
        SQL_TYPE = "TIMESTAMP"

    def to_python_value(self, value: Any) -> Optional[datetime.datetime]:
        """Convert database value to Python datetime."""
        value = super().to_python_value(value)
        return to_naive(value) if value is not None else None

    def to_db_value(
        self,
        value: Optional[datetime.datetime],
        instance: "Union[Type[Model], Model]",
    ) -> Optional[datetime.datetime]:
        """Convert Python datetime to database value."""
        value = super().to_db_value(value, instance)
        return to_naive(value) if value is not None else None


class TopicCategory(Model):
    id = fields.IntField(pk=True)
    externalId = fields.CharField(max_length=255, unique=True)
    name = fields.CharField(max_length=255, null=True)
    color = fields.CharField(max_length=255, null=True)
    slug = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    topicUrl = fields.CharField(max_length=255, null=True)
    filterable = fields.BooleanField(default=False)

    topics: fields.ReverseRelation["Topic"]

    class Meta:
        table = "TopicCategory"


class RawTopic(Model):
    id = fields.IntField(pk=True)
    externalId = fields.CharField(max_length=255, unique=True)
    url = fields.CharField(max_length=255, unique=True)
    type = fields.CharField(max_length=255)
    rawData = fields.JSONField()
    lastUpdatedAt = NaiveDatetimeField()
    lastSummarizedAt = NaiveDatetimeField()

    topics: fields.ReverseRelation["Topic"]

    class Meta:
        table = "RawTopic"


class RelatedTopics(Model):
    from_topic = fields.ForeignKeyField(
        "models.Topic", source_field="fromTopicId", related_name="related_topics_from"
    )
    to_topic = fields.ForeignKeyField(
        "models.Topic", source_field="toTopicId", related_name="related_topics_to"
    )

    class Meta:
        table = "RelatedTopics"
        unique_together = (("from_topic", "to_topic"),)


class Topic(Model):
    id = fields.IntField(pk=True)
    externalId = fields.CharField(max_length=255, unique=True)
    url = fields.CharField(max_length=255, unique=True)
    title = fields.CharField(max_length=255)
    username = fields.CharField(max_length=255)
    displayUsername = fields.CharField(max_length=255)
    category = OneToOneFieldInstance(
        "models.TopicCategory",
        related_name="topics",
        null=True,
        source_field="categoryId",
        to_field="id",
    )
    rawTopic = OneToOneFieldInstance(
        "models.RawTopic",
        related_name="topics",
        null=True,
        source_field="rawTopicId",
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
    snapshotProposal = fields.OneToOneField(
        "models.SnapshotProposal",
        related_name="topic",
        null=True,
        source_field="snapshotProposalId",
        to_field="id",
    )
    relatedTopics = fields.ManyToManyField(
        "models.Topic",
        through="RelatedTopics",
        forward_key="toTopicId",
        backward_key="fromTopicId",
        related_name="related_to_topics",
    )

    class Meta:
        table = "Topic"


class SnapshotProposal(Model):
    id = fields.IntField(pk=True)
    externalId = fields.CharField(max_length=255, unique=True)
    spaceId = fields.CharField(max_length=255)
    spaceName = fields.CharField(max_length=255)
    title = fields.CharField(max_length=255)
    author = fields.CharField(max_length=255)
    choices = fields.JSONField()
    state = fields.CharField(max_length=255)
    votes = fields.IntField()
    end = NaiveDatetimeField()
    start = NaiveDatetimeField()
    type = fields.CharField(max_length=255)
    body = fields.TextField()
    discussion = fields.CharField(max_length=255, null=True)
    quorum = fields.FloatField(null=True)
    quorumType = fields.CharField(max_length=255, null=True)
    snapshot = fields.CharField(max_length=255)
    scores = fields.JSONField()
    winningOption = fields.CharField(max_length=255, null=True)
    createdAt = NaiveDatetimeField(auto_now_add=True)
    updatedAt = NaiveDatetimeField(auto_now=True)
    topic: fields.ReverseRelation["Topic"]

    class Meta:
        table = "SnapshotProposal"


class AgoraProposal(Model):
    id = fields.IntField(pk=True)
    externalId = fields.CharField(max_length=255, unique=True)
    proposer = fields.CharField(max_length=255)
    snapshotBlockNumber = fields.IntField()
    createdTime = NaiveDatetimeField()
    startTime = NaiveDatetimeField()
    endTime = NaiveDatetimeField()
    cancelledTime = NaiveDatetimeField(null=True)
    executedTime = NaiveDatetimeField(null=True)
    markdownTitle = fields.TextField()
    description = fields.TextField()
    quorum = fields.CharField(max_length=255)
    approvalThreshold = fields.CharField(max_length=255, null=True)
    proposalData = fields.JSONField()
    unformattedProposalData = fields.TextField(null=True)
    proposalResults = fields.JSONField()
    proposalType = fields.CharField(max_length=255)
    status = fields.CharField(max_length=255)
    createdTransactionHash = fields.CharField(max_length=255, null=True)
    cancelledTransactionHash = fields.CharField(max_length=255, null=True)
    executedTransactionHash = fields.CharField(max_length=255, null=True)
    createdAt = NaiveDatetimeField(auto_now_add=True)
    updatedAt = NaiveDatetimeField(auto_now=True)

    class Meta:
        table = "AgoraProposal"


class RawTopicSummary(Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255, unique=True)
    data = fields.JSONField()
    error = fields.BooleanField(default=False)
    createdAt = NaiveDatetimeField(auto_now_add=True)
    updatedAt = NaiveDatetimeField(auto_now=True)

    class Meta:
        table = "RawTopicSummary"
