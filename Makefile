prepare:
	@echo "Preparing DB..."
	@docker-compose up -d
	$(MAKE) -C www migrate
	$(MAKE) -C pkg/op-forum-agg seed_categories
	@echo "Done."

seed_topics:
	@echo "Seeding topics..."
	prepare
	$(MAKE) -C pkg/op-forum-agg seed_topics

seed_snapshot:
	@echo "Seeding snapshot..."
	$(MAKE) -C pkg/op-forum-agg seed_snapshot