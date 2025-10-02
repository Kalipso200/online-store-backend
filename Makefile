.PHONY: test test-unit test-integration test-coverage test-report clean-test

# Запуск всех тестов
test:
	docker-compose -f docker-compose.test.yml down
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Запуск unit тестов
test-unit:
	docker-compose -f docker-compose.test.yml run test-runner pytest tests/ -m "not slow" -v

# Запуск интеграционных тестов
test-integration:
	docker-compose -f docker-compose.test.yml run test-runner pytest tests/ -m "slow" -v

# Запуск с покрытием
test-coverage:
	docker-compose -f docker-compose.test.yml run test-runner pytest --cov=app --cov-report=html --cov-report=xml -v

# Генерация отчета
test-report:
	docker-compose -f docker-compose.test.yml run test-runner pytest --junitxml=reports/junit.xml -v

# Очистка тестовых данных
clean-test:
	docker-compose -f docker-compose.test.yml down -v
	rm -rf reports/htmlcov
	rm -f reports/junit.xml
	rm -f reports/coverage.xml

# Запуск конкретного тестового файла
test-file:
	docker-compose -f docker-compose.test.yml run test-runner pytest $(FILE) -v

# Запуск тестов с определенным маркером
test-mark:
	docker-compose -f docker-compose.test.yml run test-runner pytest -m $(MARK) -v