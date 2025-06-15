# WalletWatchdog

**WalletWatchdog** — поведенческий анализатор Bitcoin-кошельков.

## Возможности

- Обнаруживает подозрительное поведение:
  - Молниеносные переводы после получения средств
  - Поведение, типичное для "горячих" кошельков
- Выводит время между входящими и исходящими транзакциями

## Установка

```bash
pip install -r requirements.txt
```

## Использование

```bash
python walletwatchdog.py <bitcoin_address>
```

Пример:

```bash
python walletwatchdog.py 1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY
```

## Лицензия

MIT License
