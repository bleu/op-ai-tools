init:
	@poetry install
	@poetry shell
	@aerich init -t op_forum_agg.config.TORTOISE_ORM

seed_categories:
	@poetry install
	@poetry run sync_categories

seed_topics:
	@poetry install
	@poetry run sync_raw_posts
	@poetry run sync_topics
