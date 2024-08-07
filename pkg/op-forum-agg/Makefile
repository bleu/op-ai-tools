init:
	@poetry install
	@poetry shell
	@aerich init -t op_forum_agg.config.TORTOISE_ORM

seed_categories:
	@poetry install
	@poetry run sync categories

seed_topics:
	@poetry install
	@poetry run sync raw_threads
	@poetry run sync forum_posts

seed_snapshot_proposals:
	@poetry install
	@poetry run sync snapshot_proposals

seed_agora_proposals:
	@poetry install
	@poetry run sync agora_proposals

seed_all: seed_categories seed_topics seed_snapshot_proposals seed_agora_proposals