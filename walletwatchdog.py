"""
WalletWatchdog: Мониторинг поведения Bitcoin-адреса на предмет подозрительных шаблонов.
"""

import requests
import argparse
from datetime import datetime
import time

def get_address_data(address):
    url = f"https://api.blockchair.com/bitcoin/dashboards/address/{address}?transaction_details=true"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Ошибка получения данных адреса.")
    return r.json()["data"][address]["transactions"]

def get_transaction_data(txid):
    url = f"https://api.blockchair.com/bitcoin/raw/transaction/{txid}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()["data"][txid]["decoded_raw_transaction"]

def parse_timestamp(txid):
    url = f"https://api.blockchair.com/bitcoin/transactions?q=hash:{txid}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    try:
        return r.json()["data"][0]["time"]
    except:
        return None

def analyze_behavior(address):
    print(f"🕵️ Анализ поведения адреса: {address}")
    txs = get_address_data(address)
    incoming = []
    outgoing = []

    for txid in txs[:30]:
        tx_data = get_transaction_data(txid)
        if not tx_data:
            continue

        vouts = tx_data.get("vout", [])
        vins = tx_data.get("vin", [])
        total_out = sum(float(v.get("value", 0)) for v in vouts if address in v.get("script_pub_key", {}).get("addresses", []))
        total_in = 0

        for vin in vins:
            prevout = vin.get("prev_out", {})
            if address in prevout.get("addresses", []):
                total_in += float(prevout.get("value", 0))

        timestamp = parse_timestamp(txid)
        if not timestamp:
            continue

        ts = int(time.mktime(datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").timetuple()))
        direction = "in" if total_out > 0 and total_in == 0 else "out" if total_in > 0 else "unknown"

        if direction == "in":
            incoming.append((ts, total_out))
        elif direction == "out":
            outgoing.append((ts, total_in))

    # Анализ скорости оборота
    if incoming and outgoing:
        time_diffs = []
        for in_tx in incoming:
            in_time = in_tx[0]
            for out_tx in outgoing:
                out_time = out_tx[0]
                if 0 < out_time - in_time < 86400:
                    time_diffs.append(out_time - in_time)
                    break
        if time_diffs:
            avg_delay = sum(time_diffs) / len(time_diffs)
            print(f"⚠️ Среднее время между входом и выходом: {avg_delay/60:.2f} минут.")
            if avg_delay < 600:
                print("🔥 Подозрение на горячий кошелёк (hot wallet).")
        else:
            print("ℹ️ Нет быстрых исходящих транзакций после входящих.")
    else:
        print("Недостаточно данных для анализа оборота.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WalletWatchdog — анализирует поведение кошелька на подозрительность.")
    parser.add_argument("address", help="Bitcoin-адрес")
    args = parser.parse_args()
    analyze_behavior(args.address)
