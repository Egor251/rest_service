# rest_service

Для rest_api использовался FastAPI, motor, pydantic
Проверка на соответствие user_id и traget_id через regexp
Для target_id так же используется валидатор, при несоответствии target_id требованиям сервис генерирует случайное значение 

Google по неясным причинам не даёт подключиться к smtp серверу, для теста отправки email рекомендуется использовать другой smtp server, однако web сервис не ложится при проблемах с smtp

после сборки docker_compose сервис стартует на localhost:1235
для тестирования rest api можно воспользоваться встроенным в fastapi сервисом документации по адресу /docs
