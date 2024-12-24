## Сервис `filtranator`
Сервис представляет собой приложение на Python (Flask), которое позволяет  регистрироваться, логиниться и загружать картинки на сервер, после чего применять на них фильтры.
Флаг хранится в поле `flag` в info метаданных каждой картинки, а также его можно прочитать c картинки напрямую.
Также присутствует функциональность получения картинки для авторизованного пользователя.

## Уязвимости сервиса `filtranator`
1. SQL injection в авторизации (Функция login).
2. Stack overflow в бинарном приложении filterer. (Можно его разреверсить)


В папке binary_rce содержится эксплойт, который позволяет пользователю записать и исполнить произвольный шеллкод( вы сами можете написать себе полезную нагрузку).

## DoS
Если попытаться сделать неправильную sql иньекцию, то подключение к бд сломается и сервис перестанет нормально работать. Лечится перезапуском или запретом спецсимволов в регистрации или в логине.