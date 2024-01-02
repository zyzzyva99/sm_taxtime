import sqlite3
import csv
import argparse
from datetime import datetime, timezone
import sys

def bech32_to_hex(bech32_address):
    CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

    def bech32_decode(bech32_addr):
        hrp, data = bech32_addr.lower().rsplit('1', 1)
        data = [CHARSET.find(c) for c in data]
        return hrp, data

    def convertbits(data, frombits, tobits, pad=True):
        acc = 0
        bits = 0
        ret = []
        maxv = (1 << tobits) - 1
        max_acc = (1 << (frombits + tobits - 1)) - 1
        for value in data:
            if value < 0 or (value >> frombits):
                return None
            acc = ((acc << frombits) | value) & max_acc
            bits += frombits
            while bits >= tobits:
                bits -= tobits
                ret.append((acc >> bits) & maxv)
        if pad:
            if bits:
                ret.append((acc << (tobits - bits)) & maxv)
        elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
            return None
        return ret

    hrp, data = bech32_decode(bech32_address)
    if data is None or hrp not in ['sm']:
        raise ValueError("Invalid bech32 address")

    decoded_bytes = convertbits(data[:-6], 5, 8, False)
    if decoded_bytes is None:
        raise ValueError("Error in bech32 conversion")

    return bytes(decoded_bytes).hex()

def calculate_layer_from_date(date, genesis_date_str="2023-07-14T08:00:00+00:00", layer_interval=300):
    genesis_date = datetime.fromisoformat(genesis_date_str)

    # Ensure the input date is also offset-aware (UTC)
    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        date = date.replace(tzinfo=timezone.utc)

    layer = int((date - genesis_date).total_seconds() / layer_interval)
    return layer

def query_transactions(db_path, decoded_coinbase, start_date=None, end_date=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    reward_query = """
    SELECT r.layer, r.total_reward, r.layer_reward, l.id
    FROM rewards r
    INNER JOIN layers l ON r.layer = l.id
    WHERE lower(hex(r.coinbase)) = ?
    """
    params = [decoded_coinbase.lower()]

    if start_date is not None:
        start_layer = calculate_layer_from_date(start_date)
        reward_query += " AND r.layer >= ?"
        params.append(start_layer)

    if end_date is not None:
        end_layer = calculate_layer_from_date(end_date)
        reward_query += " AND r.layer <= ?"
        params.append(end_layer)

    cursor.execute(reward_query, params)
    rewards = cursor.fetchall()

    processed_rewards = []
    for reward in rewards:
        layer, total_reward, layer_reward, layer_id = reward
        reward_date = datetime.utcfromtimestamp(layer_id * 300 + 1689321600).strftime('%Y-%m-%d %H:%M:%S')

        processed_reward = (
            "Reward",
            layer_reward / 1000000000,  # SMH amount
            "SMH",
            "",  # SellAmount
            "",  # SellCurrency
            0,  # FeeAmount
            "",  # FeeCurrency
            "",  # Exchange
            "",  # Group
            f"Layer Reward from Layer {layer_id}",  # Comment
            reward_date  # Date
        )
        processed_rewards.append(processed_reward)

    conn.close()
    return processed_rewards

def export_to_csv(transactions, filename=None):
    writer = csv.writer(sys.stdout if filename is None else open(filename, mode='w', newline=''))
    headers = ["Type", "BuyAmount", "BuyCurrency", "SellAmount", "SellCurrency", 
               "FeeAmount", "FeeCurrency", "Exchange", "Group", "Comment", "Date"]
    writer.writerow(headers)
    
    for transaction in transactions:
        writer.writerow(transaction)

    if filename:
        print(f"Export completed successfully. Data written to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Export Spacemesh crypto transactions.')
    parser.add_argument('coinbase', type=str, help='Coinbase address in bech32 format')
    parser.add_argument('--start_date', type=str, help='Start date (inclusive), format YYYY-MM-DD', default=None)
    parser.add_argument('--end_date', type=str, help='End date (inclusive), format YYYY-MM-DD', default=None)
    parser.add_argument('--db_path', type=str, help='Path to the SQLite database file', default=None)
    parser.add_argument('--output_file', type=str, help='Path to output CSV file', default=None)

    args = parser.parse_args()

    if args.start_date:
        args.start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    if args.end_date:
        args.end_date = datetime.strptime(args.end_date, '%Y-%m-%d')

    decoded_coinbase = bech32_to_hex(args.coinbase)

    transactions = query_transactions(args.db_path, decoded_coinbase, args.start_date, args.end_date)
    export_to_csv(transactions, args.output_file)

if __name__ == "__main__":
    main()