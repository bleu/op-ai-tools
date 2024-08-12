prepare:
	@echo "Preparing DB..."
	@docker-compose up -d
	$(MAKE) -C www migrate
	$(MAKE) -C pkg/op-data seed_categories
	@echo "Done."

seed_topics: prepare
	@echo "Seeding topics..."
	$(MAKE) -C pkg/op-data seed_topics

seed_all:
	@echo "Seeding all data... This will take a while 😬"
	$(MAKE) -C pkg/op-data seed_all
