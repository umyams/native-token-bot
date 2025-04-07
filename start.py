import json
import random
import time
from datetime import datetime
from web3 import Web3

# === CONFIG ===
CUSTOM_RPC = "https://your.custom.rpc"
DELAY_BETWEEN_TX = (10, 30)  # Random delay in seconds between transactions

w3 = Web3(Web3.HTTPProvider(CUSTOM_RPC))

# === LOAD DATA ===
with open("private_keys.txt", "r") as f:
    private_keys = [line.strip() for line in f if line.strip()]
with open("recipients.txt", "r") as f:
    recipients = [line.strip() for line in f if line.strip()]

# === MAIN LOOP ===
while True:
    start_time = time.time()

    # Ask user how many transactions
    tx_count = int(input("How many transactions to send this cycle? "))

    used_combinations = set()
    transactions_sent = 0

    while transactions_sent < tx_count:
        sender_index = random.randint(0, len(private_keys) - 1)
        recipient = random.choice(recipients)
        private_key = private_keys[sender_index]
        account = w3.eth.account.from_key(private_key)
        sender = account.address

        combo_key = f"{sender}->{recipient}"
        if combo_key in used_combinations or sender.lower() == recipient.lower():
            continue  # Skip if already used or same address
        used_combinations.add(combo_key)

        try:
            nonce = w3.eth.get_transaction_count(sender)
            gas_price = w3.eth.gas_price
            value = w3.to_wei(0.001, 'ether')  # Change value as needed

            tx = {
                'nonce': nonce,
                'to': recipient,
                'value': value,
                'gas': 21000,
                'gasPrice': gas_price,
                'chainId': w3.eth.chain_id
            }

            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"[{transactions_sent + 1}/{tx_count}] Sent from {sender[:6]}... to {recipient[:6]}... | Tx Hash: {tx_hash.hex()}")

            transactions_sent += 1
            time.sleep(random.randint(*DELAY_BETWEEN_TX))

        except Exception as e:
            print(f"❌ Error sending from {sender[:6]}...: {e}")
            continue

    end_time = time.time()
    duration = end_time - start_time
    one_day_seconds = 86400
    wait_time = max(one_day_seconds - duration, 0)

    print(f"\n✅ All {tx_count} transactions complete.")
    print(f"⏱️ Took {round(duration, 2)} seconds.")
    print(f"⏳ Waiting {round(wait_time / 60, 2)} minutes until next cycle...\n")

    time.sleep(wait_time)
