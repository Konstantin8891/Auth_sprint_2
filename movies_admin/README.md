* генерация requirements.txt из poetry(файл с основными зависимостями)
```bash
poetry export -f requirements.txt --only main --without-hashes --output requirements.txt
```
* генерация зависимостей для разработки requirements_dev.txt из poetry(файл с основными зависимостями для локальной разработки)
```bash
poetry export -f requirements.txt --only dev --without-hashes --output requirements_dev.txt --with dev
```
* генерация зависимостей для тестовой среды requirements_test.txt из poetry(файл с основными зависимостями для тестовой среды)
```bash
poetry export -f requirements.txt --only test --without-hashes --output requirements_test.txt --with test
```
