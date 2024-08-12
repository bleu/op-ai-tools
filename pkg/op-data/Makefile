init:
	@poetry install
	@poetry shell

seed_categories:
	@poetry install
	@poetry run sync categories

seed_topics:
	@poetry install
	@poetry run sync raw_topics
	# @poetry run sync topics

seed_snapshot:
	@poetry install
	@poetry run sync snapshot

seed_agora:
	@poetry install
	@poetry run sync agora

seed_all: seed_categories seed_topics seed_snapshot seed_agora