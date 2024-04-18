import hashlib
import time

class Transaction:
    def __init__(self, sender, receiver, amount, fee=0.01, signatures=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.fee = fee
        self.signatures = signatures or []
        self.timestamp = time.time()  

    def __repr__(self):
        return f"{self.sender} -> {self.receiver}: {self.amount} BTC (Fee: {self.fee} BTC,Signatures: {self.signatures}, Timestamp: {self.timestamp})"

    def add_signature(self, signature):
        self.signatures.append(signature)
        return self

    def is_multi_signature_valid(self, required_signers):
        return len(self.signatures) >= required_signers

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = f"{self.index}{self.transactions}{self.timestamp}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        assert difficulty >= 1
        prefix = '0' * difficulty
        while not self.hash.startswith(prefix):
            self.nonce += 1
            self.hash = self.compute_hash()

class Blockchain:
    def __init__(self, difficulty=2):
        self.chain = []
        self.transactions = []
        self.difficulty = difficulty
        self.create_genesis_block()
        self.mining_reward = 10
        self.balances = {'Reward': 0}  

    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def add_transaction(self, transaction, contract=None):
        if contract and not contract.evaluate(transaction):
            return False
        if transaction.sender != transaction.receiver and self.validate_transaction(transaction):
            transaction.amount -= transaction.fee
            self.transactions.append(transaction)
            return True
        return False

    def validate_transaction(self, transaction):
        required_signers = 2
        if (self.balances.get(transaction.sender, 0) >= transaction.amount + transaction.fee) and \
           transaction.is_multi_signature_valid(required_signers):
            return True
        return False

    def mine_transactions(self, miner_address):
        if not self.transactions:
            return False
        reward_transaction = Transaction("Reward", miner_address, self.mining_reward)
        self.transactions.append(reward_transaction)
        last_block = self.chain[-1]
        new_block = Block(len(self.chain), self.transactions, time.time(), last_block.hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.update_balances(new_block.transactions)
        self.transactions = []
        return True

    def update_balances(self, transactions):
        for tx in transactions:
            if tx.sender != "Reward":
                self.balances[tx.sender] -= (tx.amount + tx.fee)
            self.balances[tx.receiver] = self.balances.get(tx.receiver, 0) + tx.amount

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.compute_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

def user_interface():
    blockchain.balances["Alice"] = 100  # Initialize Alice's balance for testing
    blockchain.balances["Bob"] = 50  # Initialize Bob's balance for testing
    while True:
        print("1. Add Transaction")
        print("2. Mine Transactions")
        print("3. Show Blockchain")
        print("4. Show Pending Transactions")
        print("5. Exit")
        choice = input("Choose an action: ")
        if choice == '1':
            sender = input("Enter sender address: ")
            receiver = input("Enter receiver address: ")
            amount = float(input("Enter amount: "))
            tx = Transaction(sender, receiver, amount)
            num_signatures = int(input("Enter number of signatures: "))
            for _ in range(num_signatures):
                signature = input("Enter signature: ")
                tx.add_signature(signature)
            if blockchain.add_transaction(tx):
                print("Transaction added!")
            else:
                print("Failed to add transaction.")
                print(f"Required Signatures: 2, Provided: {len(tx.signatures)}")
                print(f"Sender Balance: {blockchain.balances.get(sender, 0)}, Required: {amount + tx.fee}")
        elif choice == '2':
            miner_address = input("Enter miner address: ")
            if blockchain.mine_transactions(miner_address):
                print("New block mined!")
            else:
                print("Mining failed or no transactions to mine.")
        elif choice == '3':
            for block in blockchain.chain:
                print(f"Block {block.index}:")
                print(f"Nonce: {block.nonce}")
                print(f"Hash: {block.hash}")
                print("Transactions:")
                for tx in block.transactions:
                    print(f"  {tx}")
        elif choice == '4':
            if blockchain.transactions:
                print("Pending Transactions:")
                for tx in blockchain.transactions:
                    print(tx)
            else:
                print("No pending transactions.")
        elif choice == '5':
            break

blockchain = Blockchain()
user_interface()