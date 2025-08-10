import requests
import sys
from datetime import datetime

API_URLS = {
    "bitcoin": "https://blockstream.info/api/blocks",
    "ethereum": "https://api.blockcypher.com/v1/eth/main"
}

def fetch_bitcoin_blocks(limit=5):
    blocks = requests.get(API_URLS["bitcoin"]).json()[:limit]
    results = []
    for b in blocks:
        block_hash = b["id"]
        details = requests.get(f"https://blockstream.info/api/block/{block_hash}").json()
        txs = requests.get(f"https://blockstream.info/api/block/{block_hash}/txs").json()
        
        suspicious = []
        for tx in txs:
            total_output = sum(vout["value"] for vout in tx.get("vout", []))
            if total_output > 5 * 10**8:  # > 5 BTC
                suspicious.append({
                    "txid": tx["txid"],
                    "btc": total_output / 1e8
                })
        
        results.append({
            "height": details["height"],
            "time": datetime.utcfromtimestamp(details["timestamp"]).isoformat(),
            "suspicious": suspicious
        })
    return results

def fetch_ethereum_data():
    data = requests.get(API_URLS["ethereum"]).json()
    return {
        "height": data["height"],
        "hash": data["hash"],
        "time": data["time"]
    }

def main():
    if len(sys.argv) < 2:
        print("Использование: python blockforge.py [bitcoin|ethereum]")
        sys.exit(1)
    
    network = sys.argv[1].lower()
    
    if network == "bitcoin":
        blocks = fetch_bitcoin_blocks()
        for b in blocks:
            print(f"Блок #{b['height']} — {b['time']}")
            if b["suspicious"]:
                print("  ⚠ Найдены подозрительные транзакции:")
                for tx in b["suspicious"]:
                    print(f"    TXID: {tx['txid']}, сумма: {tx['btc']} BTC")
            else:
                print("  Подозрительных транзакций нет.")
    elif network == "ethereum":
        info = fetch_ethereum_data()
        print(f"Последний блок Ethereum:")
        print(info)
    else:
        print("Неизвестная сеть. Доступные варианты: bitcoin, ethereum.")

if __name__ == "__main__":
    main()
