prepare:
	@echo "Preparing DB..."
	@docker-compose up -d
	$(MAKE) -C www migrate
	$(MAKE) -C pkg/op-forum-agg preseed
	$(MAKE) -C www seed
	@echo "Done."