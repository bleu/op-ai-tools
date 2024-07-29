from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from op_forum_agg.src.utils.db import store_data_in_db


class DataIngestInterface:
    def __init__(self, query, url):
        self.query = query
        self.url = url

    def fetch(self):
        raise NotImplementedError

    def transform(self, data):
        raise NotImplementedError

    def store(self, data):
        store_data_in_db(data, self.query)

    def execute(self):
        data = self.fetch()
        transformed_data = self.transform(data)
        self.store(transformed_data)


@dataclass
class Poster:
    extras: Optional[str]
    user_id: int
    description: str
    flair_group_id: Optional[int]
    primary_group_id: Optional[int]


@dataclass
class ActionsSummary:
    id: int
    count: int


@dataclass
class ThreadDetails:
    id: int
    slug: Optional[str] = None
    tags: Optional[List[str]] = field(default_factory=list)
    liked: Optional[bool] = None
    title: Optional[str] = None
    views: Optional[int] = None
    bumped: Optional[bool] = None
    closed: Optional[bool] = None
    pinned: Optional[bool] = None
    unseen: Optional[bool] = None
    excerpt: Optional[str] = None
    posters: Optional[List[Poster]] = field(default_factory=list)
    visible: Optional[bool] = None
    archived: Optional[bool] = None
    can_vote: Optional[bool] = None
    unpinned: Optional[bool] = None
    archetype: Optional[str] = None
    bumped_at: Optional[str] = None
    image_url: Optional[str] = None
    bookmarked: Optional[bool] = None
    created_at: Optional[str] = None
    like_count: Optional[int] = None
    category_id: Optional[int] = None
    fancy_title: Optional[str] = None
    has_summary: Optional[bool] = None
    posts_count: Optional[int] = None
    reply_count: Optional[int] = None
    featured_link: Optional[str] = None
    last_posted_at: Optional[str] = None
    pinned_globally: Optional[bool] = None
    tags_descriptions: Optional[Dict] = field(default_factory=dict)
    has_accepted_answer: Optional[bool] = None
    highest_post_number: Optional[int] = None
    last_poster_username: Optional[str] = None
    visibility_reason_id: Optional[int] = None


@dataclass
class ThreadPost:
    id: int
    name: Optional[str] = None
    read: Optional[bool] = None
    wiki: Optional[bool] = None
    admin: Optional[bool] = None
    reads: Optional[int] = None
    score: Optional[float] = None
    staff: Optional[bool] = None
    yours: Optional[bool] = None
    cooked: Optional[str] = None
    hidden: Optional[bool] = None
    user_id: Optional[int] = None
    version: Optional[int] = None
    can_edit: Optional[bool] = None
    can_vote: Optional[bool] = None
    topic_id: Optional[int] = None
    username: Optional[str] = None
    flair_url: Optional[str] = None
    moderator: Optional[bool] = None
    post_type: Optional[int] = None
    bookmarked: Optional[bool] = None
    can_delete: Optional[bool] = None
    created_at: Optional[str] = None
    deleted_at: Optional[str] = None
    flair_name: Optional[str] = None
    topic_slug: Optional[str] = None
    updated_at: Optional[str] = None
    user_title: Optional[str] = None
    can_recover: Optional[bool] = None
    edit_reason: Optional[str] = None
    flair_color: Optional[str] = None
    post_number: Optional[int] = None
    quote_count: Optional[int] = None
    trust_level: Optional[int] = None
    user_deleted: Optional[bool] = None
    readers_count: Optional[int] = None
    flair_bg_color: Optional[str] = None
    flair_group_id: Optional[int] = None
    accepted_answer: Optional[bool] = None
    actions_summary: Optional[List[ActionsSummary]] = field(default_factory=list)
    avatar_template: Optional[str] = None
    display_username: Optional[str] = None
    can_accept_answer: Optional[bool] = None
    primary_group_name: Optional[str] = None
    can_see_hidden_post: Optional[bool] = None
    can_unaccept_answer: Optional[bool] = None
    incoming_link_count: Optional[int] = None
    reply_to_post_number: Optional[int] = None
    can_view_edit_history: Optional[bool] = None
    topic_accepted_answer: Optional[bool] = None


@dataclass
class Thread:
    externalId: str
    url: str
    type: str
    rawData: Union[ThreadDetails, ThreadPost]
    id: Optional[int] = None


@dataclass
class Category:
    id: int
    externalId: str
    name: str
    color: str
    slug: str
    description: str
    topicUrl: str
    filterable: Optional[bool] = None
