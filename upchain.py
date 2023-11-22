python

# Importing the necessary libraries

import hashlib
import json
import random
import time
from datetime import datetime

# We create the Block class, which represents a block in the blockchain

class Block:
    # The class constructor accepts parameters:
    # index - block number in the chain
    # timestamp - block creation time
    # transactions - list of transactions included in the block
    # previous_hash - hash of the previous block in the chain
    # nonce - random number used to generate the block hash
    def _init_(self, index, timestamp, transactions, previous_hash, nonce):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce

    # Method that returns the hash of a block using the SHA-256 algorithm
    def hash(self):
        # Converting block attributes to a string in JSON format
        block_string = json.dumps(self._dict_, sort_keys=True)
        # Calculate the hash of a string using the hashlib library
        return hashlib.sha256(block_string.encode()).hexdigest()

# We create the Blockchain class, which represents a chain of blocks
class Blockchain:
    # The class constructor accepts parameters:
    # difficulty - the complexity of calculating a block hash is determined by the number of zeros at the beginning of the hash
    # reward - block mining reward in UPC
    def _init_(self, difficulty, reward):
        self.difficulty = difficulty
        self.reward = reward
        self.chain = [] # List of blocks in the chain
        self.pending_transactions = [] # List of pending transactions
        self.startups = {} # Startup dictionary, key - startup name, value - information about the startup
        self.tokens = {} # Token dictionary, key - token name, value - information about the token
        self.dapps = {} # DApps dictionary, key - DApp name, value - information about DApp
        self.create_genesis_block() # We create a genesis block, the first block in the chain

    # A method that creates a genesis block and adds it to the chain
    def create_genesis_block(self):
        # Create an instance of the Block class with arbitrary parameters
        genesis_block = Block(0, time.time(), [], "0", 0)
        # Adding a genesis block to the chain
        self.chain.append(genesis_block)

    # Method that returns the last block in the chain
    def get_last_block(self):
        return self.chain[-1]

    # Method that adds a new transaction to the list of pending transactions
    # Accepts parameters:
    # sender - sender's address
    # receiver - address of the recipient
    # amount - transfer amount in UPC
    # token - token name if the transfer is carried out in tokens, otherwise None
    # type - transaction type maybe "transfer", "create_startup", "create_token", "create_dapp"
    # data - additional transaction data, depending on the type
    def add_transaction(self, sender, receiver, amount, token, type, data):
        # Create a dictionary with transaction parameters
        transaction = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "token": token,
            "type": type,
            "data": data
        }
        # Adding a transaction to the list of pending transactions
        self.pending_transactions.append(transaction)
        # We return the block number in which the transaction will be included
        return self.get_last_block().index + 1

    # The method that checks the validity of the transaction takes the following parameter:
    # transaction - dictionary with transaction parameters
    def validate_transaction(self, transaction):
        # Getting transaction parameters
        sender = transaction["sender"]
        receiver = transaction["receiver"]
        amount = transaction["amount"]
        token = transaction["token"]
        type = transaction["type"]
        data = transaction["data"]
        # Checking that the sender and recipient are not None
        if sender is None or receiver is None:
            return False
        # We check that the transfer amount is positive
        if amount <= 0:
            return False
        # Checking that the transaction type is correct
        if type not in ["transfer", "create_startup", "create_token", "create_dapp"]:
            return False
        # We check that the token exists if the transfer is carried out in tokens
        if token is not None and token not in self.tokens:
            return False
        # We check that the sender has enough funds for the transfer
        if not self.has_enough_balance(sender, amount, token):
            return False
        # We check that the transaction data is correct, depending on the type
        if type == "create_startup":
            # Checking that the transaction data is a dictionary
            if not isinstance(data, dict):
                return False
            # Checking that the dictionary contains the necessary keys
            if "name" not in data or "description" not in data or "start_date" not in data or "end_date" not in data or "goal" not in data:
                return False
            # Checking that the startup name is unique
            if data["name"] in self.startups:
                return False
            # Checking that the startup description is not empty
            if data["description"] == "":
                return False
            # We check that the start and end dates of fundraising are correct
            try:
                start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
                end_date = datetime.strptime(data["end_date"], "%Y-%m-%d")
                if start_date > end_date:
                    return False
            except ValueError:
                return False
            # We check that the fundraising goal is positive
            if data["goal"] <= 0:
                return False
        elif type == "create_token":
            # Checking that the transaction data is a dictionary
            if not isinstance(data, dict):
                return False
            # Checking that the dictionary contains the necessary keys
            if "name" not in data or "symbol" not in data or "supply" not in data:
                return False
            # Checking that the token name and symbol are unique
            if data["name"] in self.tokens or data["symbol"] in self.tokens:
                return False
            # Проверяем, что общее количество токенов положительно
            if data["supply"] <= 0:
                return False
        elif type == "create_dapp":
            # Checking that the transaction data is a dictionary
            if not isinstance(data, dict):
                return False
            # Checking that the dictionary contains the necessary keys
            if "name" not in data or "description" not in data or "code" not in data:
                return False
            # Checking that the DApp name is unique
            if data["name"] in self.dapps:
                return False
            # Checking that the DApp description and code are not empty
        if data["description"] == "" or data["code"] == "":
                return False
        # If all checks pass, return True
        return True

    # The method that checks that the address has enough funds for the transfer takes the following parameters:
    # address - address who wants to make a transfer
    # amount - transfer amount in UPC or tokens
    # token - token name if the transfer is carried out in tokens, otherwise None
    def has_enough_balance(self, address, amount, token):
        # We get the address balance in UPC or tokens
        balance = self.get_balance(address, token)
        # Compare balance and transfer amount
        return balance >= amount

    # The method that returns the address balance in UPC or tokens takes the following parameters:
    # address - the address for which you want to get the balance
    # token - token name, if you need to get the balance in tokens, otherwise None
    def get_balance(self, address, token):
        # Initialize the balance to zero
        balance = 0
        # We go through all the blocks in the chain
        for block in self.chain:
            # We go through all transactions in the block
            for transaction in block.transactions:
                # We check that the transaction refers to the required token
                if transaction["token"] == token:
                    # Checking whether the address is the sender or recipient of the transaction
                    if transaction["sender"] == address:
                        # Reduce the balance by the transaction amount
                        balance -= transaction["amount"]
                    elif transaction["receiver"] == address:
                        # We increase the balance by the transaction amount
                        balance += transaction["amount"]
        # We return the balance
        return balance

    # The method that mines a new block and adds it to the chain takes the following parameter:
    # miner_address - address of the miner who will receive a reward for mining
    def mine_block(self, miner_address):
        # We get the number, time and hash of the last block in the chain
        last_block = self.get_last_block()
        last_index = last_block.index
        last_hash = last_block.hash()
        timestamp = time.time()
        # Create a list to store valid transactions
        valid_transactions = []
        # We go through the list of pending transactions
        for transaction in self.pending_transactions:
            # Checking the validity of the transaction
            if self.validate_transaction(transaction):
                # Add the transaction to the list of valid ones
                valid_transactions.append(transaction)
        # Add a transaction with a mining reward to the beginning of the list of valid transactions
        reward_transaction = {
            "sender": None,
            "receiver": miner_address,
            "amount": self.reward,
            "token": None,
            "type": "transfer",
            "data": None
        }
        valid_transactions.insert(0, reward_transaction)
        # Initialize the nonce to zero
        nonce = 0
        # Create an instance of the Block class with parameters
        new_block = Block(last_index + 1, timestamp, valid_transactions, last_hash, nonce)
        # While the hash of the new block does not satisfy the complexity condition, we increase the nonce and recalculate the hash
        while not new_block.hash().startswith("0" * self.difficulty):
            nonce += 1
            new_block.nonce = nonce
        # Adding a new block to the chain
        self.chain.append(new_block)
        # Clearing the list of pending transactions
        self.pending_transactions = []
        # We update information about startups, tokens and DApps in accordance with transactions in the new block
        self.update_info(new_block)
        # Returning a new block
        return new_block

    # The method, which updates information about startups, tokens and DApps according to transactions in the block, takes the parameter:
    # block - block class instance
    def update_info(self, block):
        # We go through all transactions in the block
        for transaction in block.transactions:
            # Getting the transaction type and data
            type = transaction["type"]
            data = transaction["data"]
            # If the transaction type is the creation of a startup
            if type == "create_startup":
                # Adding startup information to the startup dictionary
                self.startups[data["name"]] = data
            # If the transaction type is token creation
            elif type == "create_token":
                # Adding information about the token to the token dictionary
                self.tokens[data["name"]] = data
                self.tokens[data["symbol"]] = data
            # If the transaction type is DApp creation
            elif type == "create_dapp":
                # Adding information about DApps to the DApps dictionary
                self.dapps[data["name"]] = data

    # The method that checks the validity of the block chain takes the following parameter:
    # chain - list of blocks to check
    def validate_chain(self, chain):
        # Checking that the chain is not empty
        if len(chain) == 0:
            return False
        # We check that the first block in the chain is a genesis block
        genesis_block = chain[0]
        if genesis_block.index != 0 or genesis_block.previous_hash != "0" or genesis_block.nonce != 0:
            return False
        # We go through all the blocks in the chain, starting from the second
        for i in range(1, len(chain)):
            # We get the current and previous blocks
            current_block = chain[i]
            previous_block = chain[i-1]
            # We check that the index of the current block is one greater than the index of the previous block
            if current_block.index != previous_block.index + 1:
                return False
            # We check that the hash of the previous block in the current block matches the real hash of the previous block
            if current_block.previous_hash != previous_block.hash():
              if data["description"] == "" or data["code"] == "":
                return False
        # If all checks pass, return True
        return True

    # The method that checks that the address has enough funds for the transfer takes the following parameters:
    # address - address who wants to make a transfer
    # amount - transfer amount in UPC or tokens
    # token - token name if the transfer is carried out in tokens, otherwise None
    def has_enough_balance(self, address, amount, token):
        # We get the address balance in UPC or tokens
        balance = self.get_balance(address, token)
        # Compare the balance with the transfer amount
        if balance >= amount:
            return True
        else:
            return False

    # The method that returns the address balance in UPC or tokens takes the following parameters:
    # address - address for which you need to receive the balance
    # token - token name, if you need to get the balance in tokens, otherwise None
    def get_balance(self, address, token):
        # Initialize the balance to zero
        balance = 0
        # We go through all the blocks in the chain
        for block in self.chain:
            # We go through all transactions in the block
            for transaction in block.transactions:
                # We check that the transaction refers to the required token
                if transaction["token"] == token:
                    # Checking whether the address is the sender or recipient of the transaction
                    if transaction["sender"] == address:
                        # Reduce the balance by the transaction amount
                        balance -= transaction["amount"]
                    elif transaction["receiver"] == address:
                        # We increase the balance by the transaction amount
                        balance += transaction["amount"]
        # We return the balance
        return balance

    # The method that mines a new block and adds it to the chain takes the following parameter:
    # miner_address - address of the miner who will receive a reward for mining
    def mine_block(self, miner_address):
        # We get the number, time and hash of the last block in the chain
        last_block = self.get_last_block()
        last_index = last_block.index
        last_hash = last_block.hash()
        timestamp = time.time()
        # Creating a list of transactions for a new block
        transactions = []
        # Add a transaction with a mining reward to the list
        reward_transaction = {
            "sender": None,
            "receiver": miner_address,
            "amount": self.reward,
            "token": None,
            "type": "transfer",
            "data": None
        }
        transactions.append(reward_transaction)
        # Add pending transactions to the list, checking their validity
        for transaction in self.pending_transactions:
            if self.validate_transaction(transaction):
                transactions.append(transaction)
        # Initialize the nonce to zero
        nonce = 0
        # We generate a hash of a new block until it satisfies the complexity condition
        while True:
            # Create an instance of the Block class with the current parameters
            new_block = Block(last_index + 1, timestamp, transactions, last_hash, nonce)
            # We get the hash of the new block
            new_hash = new_block.hash()
            # Checking that the hash starts with the required number of zeros
            if new_hash.startswith("0" * self.difficulty):
                # Adding a new block to the chain
                self.chain.append(new_block)
                # Clearing the list of pending transactions
                self.pending_transactions = []
                # We update information about startups, tokens and DApps, depending on the type of transaction
                for transaction in transactions:
                    if transaction["type"] == "create_startup":
                        # Adding a startup to the startup dictionary
                        self.startups[transaction["data"]["name"]] = transaction["data"]
                    elif transaction["type"] == "create_token":
                        # Adding a token to the token dictionary
                        self.tokens[transaction["data"]["name"]] = transaction["data"]
                        # We transfer the total number of tokens to the creator’s address
                        self.add_transaction(None, transaction["sender"], transaction["data"]["supply"], transaction["data"]["name"], "transfer", None)
                    elif transaction["type"] == "create_dapp":
                        # Adding DApps to the DApps dictionary
                        self.dapps[transaction["data"]["name"]] = transaction["data"]
                # Returning a new block
                return new_block
            # Increase the nonce by one
            nonce += 1

    # A method that checks the validity of a block chain returns True or False
    def validate_chain(self):
        # We go through all the blocks in the chain, starting from the second
        for i in range(1, len(self.chain)):
            # We get the current and previous blocks
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            # Checking that the hash of the current block is correct
            if current_block.hash() != current_block.hash():
                return False
            # We check that the hash of the previous block in the current block matches the hash of the previous block
            if current_block.previous_hash != previous_block.hash():
                return False
            # We check that the hash of the current block satisfies the complexity condition
            if not current_block.hash().startswith("0" * self.difficulty):
                return False
        # If all checks pass, return True

        return True

    # A method that returns information about a block by its number or hash takes a parameter:
    if data["description"] == "" or data["code"] == "":
              return False
              return True
                  # If all checks pass, return True

    # The method that checks that the address has enough funds for the transfer takes the following parameters:
    # address - address who wants to make a transfer
    # amount - transfer amount in UPC or tokens
    # token - token name if the transfer is carried out in tokens, otherwise None
    def has_enough_balance(self, address, amount, token):
        # Calculate the address balance in UPC or tokens
        balance = self.get_balance(address, token)
        # Compare the balance with the transfer amount
        return balance >= amount

    # The method that calculates the balance of an address in UPC or tokens takes the following parameters:
    # address - адрес, для которого вычисляется баланс
    # token - название токена, если баланс вычисляется в токенах, иначе None
    def get_balance(self, address, token):
        # Initialize the balance to zero
        balance = 0
        # We go through all the blocks in the chain
        for block in self.chain:
            # We go through all transactions in the block
            for transaction in block.transactions:
                # We check that the transaction refers to the required token
                if transaction["token"] == token:
                    # Checking whether the address is the sender or recipient of the transaction
                    if transaction["sender"] == address:
                        # Reduce the balance by the transaction amount
                        balance -= transaction["amount"]
                    elif transaction["receiver"] == address:
                        # We increase the balance by the transaction amount
                        balance += transaction["amount"]
        # We return the balance
        return balance

    # The method that mines a new block and adds it to the chain takes the following parameter:
    # miner_address - address of the miner who will receive a reward for mining
    def mine_block(self, miner_address):
        # We get the number, time and hash of the last block in the chain
        last_block = self.get_last_block()
        last_index = last_block.index
        last_hash = last_block.hash()
        timestamp = time.time()
        # Создаем список транзакций для нового блока
        transactions = []
        # Add a transaction with a mining reward to the list
        reward_transaction = {
            "sender": None,
            "receiver": miner_address,
            "amount": self.reward,
            "token": None,
            "type": "transfer",
            "data": None
        }
        transactions.append(reward_transaction)
        # Add pending transactions to the list, checking their validity
        for transaction in self.pending_transactions:
            if self.validate_transaction(transaction):
                transactions.append(transaction)
        # Initialize the nonce to zero
        nonce = 0
        # Generating a block hash using nonce
        block_hash = self.generate_hash(last_index + 1, timestamp, transactions, last_hash, nonce)
        # Repeat until the hash satisfies the complexity condition
        while not block_hash.startswith("0" * self.difficulty):
            nonce += 1
            block_hash = self.generate_hash(last_index + 1, timestamp, transactions, last_hash, nonce)
        # We create an instance of the Block class with the received parameters
        new_block = Block(last_index + 1, timestamp, transactions, last_hash, nonce)
        # Adding a new block to the chain
        self.chain.append(new_block)
        # Clearing the list of pending transactions
        self.pending_transactions = []
        # We update information about startups, tokens and DApps, depending on the type of transaction
        for transaction in transactions:
            if transaction["type"] == "create_startup":
                # Adding a startup to the startup dictionary
                self.startups[transaction["data"]["name"]] = transaction["data"]
            elif transaction["type"] == "create_token":
                # Adding a token to the token dictionary
                self.tokens[transaction["data"]["name"]] = transaction["data"]
                # We transfer the total number of tokens to the creator’s address
                self.add_transaction(None, transaction["receiver"], transaction["data"]["supply"], transaction["data"]["name"], "transfer", None)
            elif transaction["type"] == "create_dapp":
                # Adding DApps to the DApps dictionary
                self.dapps[transaction["data"]["name"]] = transaction["data"]
        # Returning a new block
        return new_block

    # The method that generates a block hash using parameters takes parameters:
    # index - block number in the chain
    # timestamp - block creation time
    # transactions - list of transactions included in the block
    # previous_hash - hash of the previous block in the chain
    # nonce - random number used to generate the block hash
    def generate_hash(self, index, timestamp, transactions, previous_hash, nonce):
        # Create a dictionary with block parameters
        block = {
            "index": index,
            "timestamp": timestamp,
            "transactions": transactions,
            "previous_hash": previous_hash,
            "nonce": nonce
        }
        # Convert the dictionary to a string in JSON format
        block_string = json.dumps(block, sort_keys=True)
        # Calculate the hash of a string using the hashlib library
        return hashlib.sha256(block_string.encode()).hexdigest()

    # The method that checks the validity of the block chain takes the following parameter:
    # chain - list of blocks to check
    def validate_chain(self, chain):
        # Checking that the chain is not empty
        if len(chain) == 0:
            return False
        # We check that the first block in the chain is a genesis block
        genesis_block = self.chain[0]
        if chain[0]._dict_ != genesis_block._dict_:
            return False
        # We go through all the blocks in the chain, starting from the second
        for i in range(1, len(chain)):
            # We get the current and previous blocks
            current_block = chain[i]
            previous_block = chain[i-1]
            # Checking that the hash of the current block is correct
            if current_block.hash() != current_block.generate_hash(current_block.index, current_block.timestamp, current_block.transactions, current_block.previous_hash, current_block.nonce):
                return False
            # We check that the hash of the previous block matches the previous_hash attribute of the current block
            if current_block.previous_hash != previous_block.hash():
                return False
            # We check that the hash of the current block satisfies the complexity condition
            if not current_block.hash().startswith("0" * self.difficulty):
                return False
            # We check that all transactions in the current block are valid
            for transaction in current_block.transactions:
                if not self.validate_transaction(transaction):
                    return False
        # If all checks pass, return True
        return True

    # A method that replaces the current block chain with a longer one, if one exists.

 # A method that replaces the current block chain with a longer one, if one exists, takes the parameter:
    # new_chain - a list of blocks that could potentially replace the current chain
    def replace_chain(self, new_chain):
        # Check that the new chain is longer than the current one
        if len(new_chain) > len(self.chain):
            # Checking that the new chain is valid
            if self.validate_chain(new_chain):
                # Replace the current chain with a new one
                self.chain = new_chain
                # Return True
                return True
        # Returning False
        return False

    # The method that returns information about a block by its hash takes the following parameter:
    # block_hash - hash of the block to be found
    def get_block_by_hash(self, block_hash):
        # We go through all the blocks in the chain
        for block in self.chain:
            # Checking whether the block hash matches the desired one
            if block.hash() == block_hash:
                # Returning the block
                return block
        # Return None if the block is not found
        return None

    # The method that returns information about a startup by its name takes a parameter:
    # startup_name - the name of the startup to be found
    def get_startup_by_name(self, startup_name):
        # Checking if the startup is in the startup dictionary
        if startup_name in self.startups:
            # We return information about the startup
            return self.startups[startup_name]
        # Return None if the startup is not found
        return None

    # A method that generates a user's address from 24 random words returns a string with the address
    def generate_address(self):
        # Create a list of words from which you can make an address
        words = ["apple", "banana", "carrot", "dog", "elephant", "fish", "giraffe", "house", "ice", "jacket", "kite", "lion", "moon", "nose", "orange", "pencil", "queen", "rainbow", "star", "tree", "umbrella", "vase", "water", "xylophone"]
        # Selecting 24 random words from the list
        random_words = random.sample(words, 24)
        # Connecting words into one line with spaces
        address = " ".join(random_words)
        # Returning the address
        return address

# We create an instance of the Blockchain class with the following parameters:
# difficulty - 4, reward - 10
up_chain = Blockchain(4, 10)

# Class to represent smart contracts
class SmartContract:

    # Class constructor
    def __init__(self, code, sender, gas_limit):
        self.code = code # Smart contract code
        self.sender = sender # Smart contract sender address
        self.gas_limit = gas_limit # Gas limit for smart contract execution
        self.gas_used = 0 # The amount of gas used when executing a smart contract
        self.state = {} # Smart contract status

    # Method for executing a smart contract
    def execute(self, blockchain, transaction):
        # Checking that the gas limit has not been exceeded
        if self.gas_used > self.gas_limit:
            return False, "Gas limit exceeded"

        # Execute smart contract code in a secure environment
        try:
            exec(self.code, globals(), locals())
        except Exception as e:
            return False, "Smart contract execution error: " + str(e)

        # Updating the state of the smart contract
        self.state = locals()

        # Returning the result of smart contract execution
        return True, "Smart contract executed successfully"

# Function for creating a smart contract
def create_smart_contract(code, sender, gas_limit):
    # Create an instance of the SmartContract class
    smart_contract = SmartContract(code, sender, gas_limit)

    # Adding a smart contract to the list of blockchain smart contracts
    blockchain.smart_contracts.append(smart_contract)

    # Returning the smart contract
    return smart_contract

# Function for calling a smart contract
def call_smart_contract(smart_contract, blockchain, transaction):
    # We execute a smart contract
    result, message = smart_contract.execute(blockchain, transaction)

    # Returning the result and message
    return result, message
