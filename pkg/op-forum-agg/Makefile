preseed:
	@poetry install
	@poetry shell
	@python op_forum_agg/src/sync/categories.py
	@python op_forum_agg/src/sync/raw_threads.py
	@python op_forum_agg/src/sync/threads.py
