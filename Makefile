.PHONY: help install test run serve search list show runbook slack clean

help:
	@echo "📚 Incident Wiki - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install Python dependencies"
	@echo "  make test          Run setup tests"
	@echo ""
	@echo "CLI Commands:"
	@echo "  make list          List all incidents"
	@echo "  make search q=<query>  Search incidents"
	@echo "  make show id=<id>   Show incident details"
	@echo "  make runbook id=<id>  Show incident runbook"
	@echo ""
	@echo "Notifications:"
	@echo "  make slack id=<id>  Send incident to Slack"
	@echo "  make email id=<id> [recipients=email@example.com]  Send via email"
	@echo "  make email-search q=<query>  Search and email results"
	@echo ""
	@echo "Server:"
	@echo "  make serve         Start Flask API server"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         Remove Python cache files"
	@echo ""
	@echo "Examples:"
	@echo "  make list"
	@echo "  make search q=database"
	@echo "  make show id=db-connection-timeout"
	@echo "  make slack id=db-connection-timeout"
	@echo "  make email id=db-connection-timeout"
	@echo "  make email id=db-connection-timeout recipients=team@example.com"

install:
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

test:
	python test_setup.py

run: test
	@echo "✅ Setup verified"

serve:
	python src/app.py

list:
	python src/cli.py list

search:
	@if [ -z "$(q)" ]; then \
		echo "❌ Usage: make search q=<query>"; \
		echo "   Example: make search q=database"; \
	else \
		python src/cli.py search "$(q)"; \
	fi

show:
	@if [ -z "$(id)" ]; then \
		echo "❌ Usage: make show id=<incident-id>"; \
		echo "   Example: make show id=db-connection-timeout"; \
	else \
		python src/cli.py show "$(id)"; \
	fi

runbook:
	@if [ -z "$(id)" ]; then \
		echo "❌ Usage: make runbook id=<incident-id>"; \
		echo "   Example: make runbook id=db-connection-timeout"; \
	else \
		python src/cli.py runbook "$(id)"; \
	fi

slack:
	@if [ -z "$(id)" ]; then \
		echo "❌ Usage: make slack id=<incident-id>"; \
		echo "   Example: make slack id=db-connection-timeout"; \
	else \
		python3 src/cli.py slack "$(id)"; \
	fi

email:
	@if [ -z "$(id)" ]; then \
		echo "❌ Usage: make email id=<incident-id> [recipients=email@example.com]"; \
		echo "   Example: make email id=db-connection-timeout"; \
		echo "   With recipients: make email id=db-connection-timeout recipients=team@example.com,oncall@example.com"; \
	else \
		if [ -z "$(recipients)" ]; then \
			python3 src/cli.py email "$(id)"; \
		else \
			python3 src/cli.py email "$(id)" "$(recipients)"; \
		fi \
	fi

email-search:
	@if [ -z "$(q)" ]; then \
		echo "❌ Usage: make email-search q=<query> [recipients=email@example.com]"; \
		echo "   Example: make email-search q=database"; \
	else \
		if [ -z "$(recipients)" ]; then \
			python3 src/cli.py email-search "$(q)"; \
		else \
			python3 src/cli.py email-search "$(q)" "$(recipients)"; \
		fi \
	fi

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cache cleaned"
