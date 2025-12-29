.PHONY: ome1 clean auditpack

ome1:
	docker compose up --build --abort-on-container-exit
	@echo "OME-1 done. receipt_ome1.json generated."
	$(MAKE) verify

clean:
	rm -f rb_ledger.sqlite3 receipt_ome1.json
	docker compose down -v --remove-orphans

auditpack:
	bash scripts/auditpack.sh

verify:
	python3 core/verify_ome1.py
