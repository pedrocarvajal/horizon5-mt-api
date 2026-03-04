# Management Commands

Connection is configured via `.env`:

- `SEED_ROOT_API_KEY` — bearer token
- `DJANGO_FORWARD_HOST` — base URL (e.g. `http://100.66.47.69:8000`)

Load before running: `source .env`

---

## Dev commands

Event commands poll for response up to 10 seconds after pushing.

### dev_push_order

```bash
python manage.py dev_push_order --account-id 11912085 --strategy 1
python manage.py dev_push_order --account-id 11912085 --strategy 1 --symbol XAUUSD --volume 0.01 --type buy --sl 1900.00 --tp 2100.00
```

### dev_modify_order

```bash
python manage.py dev_modify_order --account-id 11912085 --order-id 12345 --sl 1900.00 --tp 2100.00
```

### dev_close_order

```bash
python manage.py dev_close_order --account-id 11912085 --order-id 12345 --strategy 1
```

### dev_get_orders

```bash
python manage.py dev_get_orders --account-id 11912085
python manage.py dev_get_orders --account-id 11912085 --symbol XAUUSD
python manage.py dev_get_orders --account-id 11912085 --symbol XAUUSD --side buy --status open
```

### dev_account_info

```bash
python manage.py dev_account_info --account-id 11912085
```

### dev_get_ticker

```bash
python manage.py dev_get_ticker --account-id 11912085 --symbols XAUUSD,EURUSD
```

### dev_list_accounts

```bash
python manage.py dev_list_accounts
```

### dev_list_strategies

```bash
python manage.py dev_list_strategies
```

### dev_list_snapshots

```bash
python manage.py dev_list_snapshots --type account --account-id 11912085
python manage.py dev_list_snapshots --type strategy --strategy-id 550e8400-e29b-41d4-a716-446655440000
python manage.py dev_list_snapshots --type strategy --strategy-id 550e8400-e29b-41d4-a716-446655440000 --account-id 11912085 --per-page 10 --order-by -created_at
```

---

### dev_get_producer_credentials

```bash
python manage.py dev_get_producer_credentials
```

---

## Maintenance commands

```bash
python manage.py seed_database
python manage.py check_stuck_events
python manage.py purge_events
python manage.py purge_logs
python manage.py purge_heartbeats
python manage.py purge_account_snapshots
python manage.py purge_strategy_snapshots
python manage.py clean_expired_media
python manage.py run_scheduler
```
