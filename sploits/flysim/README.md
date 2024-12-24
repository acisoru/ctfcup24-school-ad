## Сервис `flysim`
Сервис представляет собой приложение на Python (Flask, SocketIO, gunicorn), симулирующее работу дронов - можно создать дрон, назначить ему скорость, полётный план (на какой секунде ускориться, поменять частоту) и наблюдать за его полётом (изменяются координаты каждый тик ~1сек). "Наблюдение" идёт через socket.io (websocket или polling).  
Флаг хранится в поле `secret_data`, и его можно узнать, лишь подключившись к дрону по socket.io с правильным `control_key` (штатным образом, без использования уязвимостей).  
Также присутствует функциональность получения всех созданных дронов (только id) и более детальный интерфейс (можно найти дрон с определённым label, причём получить все его данные за исключением приватных ("control_key", "secret_data", "flight_plan", "flight_log")).

## Уязвимости сервиса `flysim`
1. NoSQL injection в параметре what= (`sploit_nosql.py`). Помимо "$match", можно дописать и "$lookup", сматчив все строки (`{"$match": {"label": {"$regex": "^.*"}}}`).
2. CRC32 используется в `session_authenticator.generate(drone_id, label)` (это можно понять, отреверсив .so-шник, скомпиленный codon-ом) (`sploit_crc32.py`)
3. В flight plan можно вызвать get_var (`sploit_flight_plan.py`) помимо "стандартных" операций типа BOOSTX/BOOSTY/FIRE/SETFREQ, `func = globals().get(command_name)` - get_var входит в globals.

## DoS
`./client create --label asdf --flight-plan "BOOSTX [drone] 200\nBOOSTY [drone] 400\n"` (намеренно пропущено время запуска: не `0 BOOSTX [drone] 200`, а `BOOSTX [drone] 200`)     
Приведёт к ошибке:
```
flysim_1        | Traceback (most recent call last):
flysim_1        |   File "src/gevent/greenlet.py", line 900, in gevent._gevent_cgreenlet.Greenlet.run
flysim_1        |   File "/app/server.py", line 214, in run_update_positions
flysim_1        |     update_positions()
flysim_1        |   File "/app/server.py", line 176, in update_positions
flysim_1        |     process_flight_plan(drone, cur_time)
flysim_1        |   File "/app/flight_plans.py", line 50, in process_flight_plan
flysim_1        |     expected_time = int(parts[0])
flysim_1        |                     ^^^^^^^^^^^^^
flysim_1        | ValueError: invalid literal for int() with base 10: 'BOOSTX'
```  
При этом цикл, отвечающий за обновление данных обо всех дронах и рассылку сообщений в socket.io-комнаты, перестанет работать и чекер будет timeout-ится в ожидании сообщения, которое не поступит.
