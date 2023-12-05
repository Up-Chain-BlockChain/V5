# Importing the necessary libraries
import hashlib # for data hashing
import json # for data serialization
import time # to get timestamps
import random # to generate random numbers and words
import requests # to send and receive requests to other network nodes

# Defining constants
MAX_SUPPLY = 100000000000 # the maximum number of coins that can be mined
BURN_RATE = 0.0001 # percentage of coins burned from the transaction amount
BURN_THRESHOLD = 50000000000 # the number of coins burned, after which the burning stops
BURN_ADDRESS = "0x0000000000000000000000000000000000000000" # the address to which the burned coins are sent
MINING_REWARD = 50 # reward for mining a block in coins (The number is indicated as an example)
DIFFICULTY = 4 # initial mining difficulty (the number of zeros at the beginning of the block hash)
STARTUP_FEE = 10 # commission for adding a startup to a block in coins
NFT_FEE = 5 # commission for adding NFT to a block in coins
TOKEN_FEE = 5 # commission for adding a token to a block in coins
DAPP_FEE = 5 # commission for adding a DApp to a block in coins
WORD_LIST = ["apple", "banana", "carrot", "dog", "elephant", "fish", "giraffe", "house", "ice", "jacket", "kite", "lion", "moon", "nose", "orange", "pencil", "queen", "rainbow", "star", "tree", "umbrella", "vase", "water", "xylophone", "yarn", "zebra"] # list of words for generating addresses

# Defining the block class
class Block:
    # Class constructor
    def _init_(self, index, timestamp, transactions, previous_hash, nonce, hash):
        self.index = index # sequence number of the block in the chain
        self.timestamp = timestamp # block creation time
        self.transactions = transactions # list of transactions in the block
        self.previous_hash = previous_hash # hash of the previous block
        self.nonce = nonce # random number used for mining
        self.hash = hash # current block hash

    # Method for serializing a block into JSON format
    def to_json(self):
        return json.dumps(self._dict_, sort_keys=True)

# Defining the transaction class
class Transaction:
    # Class constructor
    def _init_(self, sender, recipient, amount, fee, data):
        self.sender = sender # sender's address
        self.recipient = recipient # address of the recipient
        self.amount = amount # transfer amount in coins
        self.fee = fee # transaction fee in coins
        self.data = data # additional transaction data (for example, information about the startup, NFT, token or DApp)
        self.hash = self.calculate_hash() # transaction hash

    # Method for calculating transaction hash
    def calculate_hash(self):
        # We serialize the transaction in JSON format and encode it into bytes
        transaction_string = json.dumps(self._dict_, sort_keys=True).encode()
        # Returning the transaction hash in hexadecimal format
        return hashlib.sha256(transaction_string).hexdigest()

# Defining the blockchain class
class Blockchain:
    # Class constructor
    def _init_(self):
        self.chain = [] # list of blocks in the chain
        self.pending_transactions = [] # list of pending transactions
        self.nodes = set() # many addresses of other network nodes
        self.burned_coins = 0 # number of coins burned
        self.create_genesis_block() # create a genesis block

    # Method for creating a genesis block
    def create_genesis_block(self):
        # Create the first block with arbitrary data
        genesis_block = Block(0, time.time(), [], "0", 0, "0")
        # Add it to the chain
        self.chain.append(genesis_block)
        # Generating the first address of the blockchain creator
        creator_address = self.generate_address()
        # We create a transaction that credits the maximum number of coins to this address
        genesis_transaction = Transaction("0", creator_address, MAX_SUPPLY, 0, None)
        # Add this transaction to the block
        genesis_block.transactions.append(genesis_transaction)

    # Method for generating a new address
    def generate_address(self):
        # Selecting 24 random words from the list
        words = random.sample(WORD_LIST, 24)
        # We connect them into one line with spaces
        address_string = " ".join(words)
        # We hash this string using SHA256 and return the result in hexadecimal format
        return hashlib.sha256(address_string.encode()).hexdigest()

    # Method to get the last block in the chain
    def get_last_block(self):
        return self.chain[-1]

    # Method for adding a new block to the chain
    def add_block(self, block):
        # We check that the block has the correct index, hash and link to the previous block
        if block.index == len(self.chain) and block.hash == block.calculate_hash() and block.previous_hash == self.get_last_block().hash:
            # Adding a block to the chain
            self.chain.append(block)
            # Clearing the list of pending transactions
            self.pending_transactions = []
            # Clearing the list of pending transactions
            return True
        else:
            # Return False if the block is invalid
            return False

    # Method for creating a new transaction
    def create_transaction(self, sender, recipient, amount, fee, data):
        # Checking that the sender and recipient have the correct address format
        if len(sender) == 64 and len(recipient) == 64:
            # We check that the amount and commission are non-negative and do not exceed the maximum number of coins
            if 0 <= amount <= MAX_SUPPLY and 0 <= fee <= MAX_SUPPLY:
                # We check that the sender has sufficient funds for the transfer
                if self.get_balance(sender) >= amount + fee:
                    # Create a new transaction
                    transaction = Transaction(sender, recipient, amount, fee, data)
                    # Add it to the list of pending transactions
                    self.pending_transactions.append(transaction)
                    # Returning the transaction hash
                    return transaction.hash
                else:
                    # Return an error message if there are insufficient funds
                    return "Insufficient funds"
            else:
                # We return an error message if the amount or commission is incorrect
                return "Invalid amount or fee"
        else:
            # Return an error message if the addresses are incorrect
            return "Invalid sender or recipient address"

    # Method to get address balance
    def get_balance(self, address):
        # Initialize the balance to zero
        balance = 0
        # We go through all the blocks in the chain
        for block in self.chain:
            # We go through all transactions in the block
            for transaction in block.transactions:
                # If the address is the sender, then we reduce the balance by the transfer amount and commission
                if transaction.sender == address:
                    balance -= transaction.amount + transaction.fee
                # If the address is the recipient, then we increase the balance by the transfer amount
                if transaction.recipient == address:
                    balance += transaction.amount
        # We return the balance
        return balance

    # Method for calculating block hash
    def calculate_hash(self, index, timestamp, transactions, previous_hash, nonce):
        # We serialize the block data into JSON format and encode it into bytes
        block_string = json.dumps([index, timestamp, transactions, previous_hash, nonce], sort_keys=True).encode()
        # Returning the block hash in hexadecimal format
        return hashlib.sha256(block_string).hexdigest()

    # Method for mining a new block
    def mine_block(self):
        # We get the index, time and hash of the last block
        last_block = self.get_last_block()
        index = last_block.index + 1
        timestamp = time.time()
        previous_hash = last_block.hash
        # Initialize nonce and hash to zero
        nonce = 0
        hash = "0"
        # While the hash does not satisfy the complexity condition, we increase the nonce and recalculate the hash
        while not hash.startswith("0" * DIFFICULTY):
            nonce += 1
            hash = self.calculate_hash(index, timestamp, self.pending_transactions, previous_hash, nonce)
        # Create a new block with the received data
        block = Block(index, timestamp, self.pending_transactions, previous_hash, nonce, hash)
        # Adding a new block to the chain
        self.add_block(block)
        # Returning a new block
        return block

    # Method for checking the validity of the chain
    def is_valid(self):
        # We go through all the blocks in the chain, starting from the secondы
        for i in range(1, len(self.chain)):
            # We get the current and previous blocks
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            # We check that the hash of the current block matches the calculated hash
            if current_block.hash != current_block.calculate_hash():
                return False
            # We check that the hash of the previous block matches the link to the previous block
            if current_block.previous_hash != previous_block.hash:
                return False
        # Return True if all blocks are valid
        return True

    # Method for adding a new node to the network
    def add_node(self, node_address):
        # Checking that the host address is in the correct format
        if node_address.startswith("http://") or node_address.startswith("https://"):
            # Adding a node address to a set of nodes
            self.nodes.add(node_address)
            # Returning a success message
            return f"Node {node_address} added to the network"
        else:
            # Returning an error message
            return "Invalid node address"

    # Method for synchronizing the chain with other network nodes
    def sync_chain(self):
        # Initialize a variable to store the longest chain
        longest_chain = None
        # Initialize a variable to store the length of the longest chain
        max_length = len(self.chain)
        # We go through all the nodes in the network
        for node in self.nodes:
            # Send a request to receive the node chain
            response = requests.get(f"{node}/chain")
            # If the request is successful
            if response.status_code == 200:
                # We get the length and chain of the node from the answer
                length = response.json()["length"]
                chain = response.json()["chain"]
                # If the length of the node chain is greater than the length of the longest chain
                if length > max_length:
                    # Update the longest chain and its length
                    longest_chain = chain
                    max_length = length
        # If the longest chain is found and it is valid
        if longest_chain and self.is_valid(longest_chain):
            # Replace our chain with the longest chain
            self.chain = longest_chain
            # Returning a success message
            return "Chain synchronized with the network"
        else:
            # We return a message that our chain is up to date
            return "Our chain is up to date"

    # Method for adding a new startup to a block
    def create_startup(self, sender, startup_name, startup_description, startup_date, fundraising_date, investment_offer, nft_info, required_funds, token_name, dapp_name, dapp_url):
        # Checking that the sender has the correct address format
        if len(sender) == 64:
            # We check that the startup name is not empty and unique
            if startup_name and not self.get_startup_by_name(startup_name):
                # We check that the required amount of funds in dollars is positive and does not exceed the maximum number of coins
                if 0 < required_funds <= MAX_SUPPLY:
                    # We check that the sender has enough funds to pay the commission for adding a startup to the block
                    if self.get_balance(sender) >= STARTUP_FEE:
                        # Creating a dictionary with startup data
                        startup_data = {
                            "startup_name": startup_name,
                            "startup_description": startup_description,
                            "startup_date": startup_date,
                            "fundraising_date": fundraising_date,
                            "investment_offer": investment_offer,
                            "nft_info": nft_info,
                            "required_funds": required_funds,
                            "token_name": token_name,
                            "dapp_name": dapp_name,
                            "dapp_url": dapp_url
                        }
                        # We create a transaction that sends a commission to the burning address and adds data about the startup to the block
                        transaction = Transaction(sender, BURN_ADDRESS, 0, STARTUP_FEE, startup_data)
                        # Adding a transaction to the list of pending transactions
                        self.pending_transactions.append(transaction)
                        # We increase the number of burned coins by commission
                        self.burned_coins += STARTUP_FEE
                        # Returning the transaction hash
                        return transaction.hash
                    else:
                        # Return an error message if there are insufficient funds
                        return "Insufficient funds"
                else:
                    # Return an error message if the required amount of funds is incorrect
                    return "Invalid required funds"
            else:
                # Return an error message if the startup name is empty or not unique
                return "Invalid or duplicate startup name"
        else:
            # Return an error message if the sender address is incorrect
            return "Invalid sender address"

    # Method to get startup by name
    def get_startup_by_name(self, startup_name):
        # We go through all the blocks in the chain
        for block in self.chain:
            # We go through all transactions in the block
            for transaction in block.transactions:
                # If the transaction contains startup data
                if transaction.data and "startup_name" in transaction.data:
                    # If the startup name matches what you are looking for
                    if transaction.data["startup_name"] == startup_name:
                        # We return data about the startup
                        return transaction.data
        # Return None if the startup is not found
        return None

    # Method for creating a new NFT into a block
    def create_nft(self, sender, nft_name, nft_description, nft_image, nft_price, nft_owner):
        # Checking that the sender has the correct address format
        if len(sender) == 64:
            # Checking that the NFT name is not empty and unique
            if nft_name and not self.get_nft_by_name(nft_name):
                # We check that the NFT price is positive and does not exceed the maximum number of coins
                if 0 < nft_price <= MAX_SUPPLY:
                    # We check that the sender has enough funds to pay the fee for adding the NFT to the block
                    if self.get_balance(sender) >= NFT_FEE:
                        # Creating a dictionary with NFT data
                        nft_data = {
                            "nft_name": nft_name,
                            "nft_description": nft_description,
                            "nft_image": nft_image,
                            "nft_price": nft_price,
                            "nft_owner": nft_owner
                        }
                        # Create a transaction that sends a fee to the burn address and adds NFT data to the block
                        transaction = Transaction(sender, BURN_ADDRESS, 0, NFT_FEE, nft_data)
                        # Adding a transaction to the list of pending transactions
                        self.pending_transactions.append(transaction)
                        # We increase the number of burned coins by commission
                        self.burned_coins += NFT_FEE
                        # Returning the transaction hash
                        return transaction.hash
                    else:
                        # Return an error message if there are insufficient funds
                        return "Insufficient funds"
                else:
                    # Returning an error message if the NFT price is incorrect
                    return "Invalid nft price"
            else:
                # Return an error message if the NFT name is empty or not unique
                return "Invalid or duplicate nft name"
        else:
            # Return an error message if the sender address is incorrect
            return "Invalid sender address"

    # Method to get NFT by name
    def get_nft_by_name(self, nft_name):
        # We go through all the blocks in the chain
        for block in self.chain:
            # We go through all transactions in the block
            for transaction in block.transactions:
                # If the transaction contains NFT data
                if transaction.data and "nft_name" in transaction.data:
                    # If the NFT name matches what you're looking for
                    if transaction.data["nft_name"] == nft_name:
                        # Returning NFT data
                        return transaction.data
        # Return None if NFT is not found
        return None

    # Method for creating a new token in a block
    def create_token(self, sender, token_name, token_symbol, token_supply, token_price, token_owner):
        # Checking that the sender has the correct address format
        if len(sender) == 64:
            # We check that the name and symbol of the token are not empty and unique
            if token_name and token_symbol and not self.get_token_by_name(token_name) and not self.get_token_by_symbol(token_symbol):
                # We check that the total quantity and price of the token are positive and do not exceed the maximum number of coins
                if 0 < token_supply <= MAX_SUPPLY and 0 < token_price <= MAX_SUPPLY:
                    # We check that the sender has enough funds to pay the commission for adding the token to the block
                    if self.get_balance(sender) >= TOKEN_FEE:
                        # Create a dictionary with token data
                        token_data = {
                            "token_name": token_name,
                            "token_symbol": token_symbol,
                            "token_supply": token_supply,
                            "token_price": token_price,
                            "token_owner": token_owner
                        }
                        # Create a transaction that sends a commission to the burn address and adds token data to the block
                        transaction = Transaction(sender, BURN_ADDRESS, 0, TOKEN_FEE, token_data)
                        # Adding a transaction to the list of pending transactions
                        self.pending_transactions.append(transaction)
                        # We increase the number of burned coins by commission
                        self.burned_coins += TOKEN_FEE
                        # Returning the transaction hash

                        return transaction.hash
                    else:
                        # Return an error message if there are insufficient funds
                        return "Insufficient funds"
                else:
                    # Return an error message if the total supply or price of a token is incorrect
                    return "Invalid token supply or price"
            else:
                # Return an error message if the token name or symbol is empty or not unique
                return "Invalid or duplicate token name or symbol"
        else:
            # Return an error message if the sender address is incorrect
            return "Invalid sender address"

    # Method for getting a token by name
    def get_token_by_name(self, token_name):
        # We go through all the blocks in the chain
        for block in self.chain:
            # We go through all transactions in the block
            for transaction in block.transactions:
                # If the transaction contains token data
                if transaction.data and "token_name" in transaction.data:
                    # If the token name matches the one you are looking for
                    if transaction.data["token_name"] == token_name:
                        # Returning token data
                        return transaction.data
        # Return None if the token is not found
        return None

    # Method for getting a token by symbol
    def get_token_by_symbol(self, token_symbol):
        # We go through all the blocks in the chain
        for block in self.chain:
            # We go through all transactions in the block
            for transaction in block.transactions:
                # If the transaction contains token data
                if transaction.data and "token_symbol" in transaction.data:
                    # If the token character matches the one you are looking for
                    if transaction.data["token_symbol"] == token_symbol:
                        # Returning token data
                        return transaction.data
        # Return None if the token is not found
        return None

    # Method for creating a new DApp in a block
    def create_dapp(self, sender, dapp_name, dapp_description, dapp_url, dapp_owner):
        # Checking that the sender has the correct address format
        if len(sender) == 64:
            # Checking that the DApp name is not empty and unique
            if dapp_name and not self.get_dapp_by_name(dapp_name):
                # Checking that the DApp URL is in the correct format
                if dapp_url.startswith("http://") or dapp_url.startswith("https://"):
                    # We check that the sender has enough funds to pay the commission for adding the DApp to the block
                    if self.get_balance(sender) >= DAPP_FEE:
                        # Creating a dictionary with data about DApp
                        dapp_data = {
                            "dapp_name": dapp_name,
                            "dapp_description": dapp_description,
                            "dapp_url": dapp_url,
                            "dapp_owner": dapp_owner
                        }
                        # Create a transaction that sends a commission to the burn address and adds data about the DApp to the block
                        transaction = Transaction(sender, BURN_ADDRESS, 0, DAPP_FEE, dapp_data)
                        # Adding a transaction to the list of pending transactions
                        self.pending_transactions.append(transaction)
                        # We increase the number of burned coins by commission
                        self.burned_coins += DAPP_FEE
                        # Returning the transaction hash
                        return transaction.hash
                    else:
                        # Return an error message if there are insufficient funds
                        return "Insufficient funds"
                else:
                    # Return an error message if the DApp URL is incorrect
                    return "Invalid dapp url"
            else:
                # Return an error message if the DApp name is empty or not unique
                return "Invalid or duplicate dapp name"
        else:
            # Return an error message if the sender address is incorrect
            return "Invalid sender address"

    # Method to get DApp by name
    def get_dapp_by_name(self, dapp_name):
        # We go through all the blocks in the chain
        for block in self.chain:
            # We go through all transactions in the block
            for transaction in block.transactions:
                # If the transaction contains DApp data
                if transaction.data and "dapp_name" in transaction.data:
                    # If the DApp name matches the searched one
                    if transaction.data["dapp_name"] == dapp_name:
                        # Returning data about the DApp
                        return transaction.data
        # Return None if DApp is not found
        return None

    # Method for receiving a transaction by hash
    def get_transaction_by_hash(self, transaction_hash):
        # We go through all the blocks in the chain
        for block in self.chain:
            # We go through all transactions in the block
            for transaction in block.transactions:
                # If the transaction hash matches the searched one
                if transaction.hash == transaction_hash:
                    # Returning the transaction
                    return transaction
        # Return None if transaction not found
        return None

    # Method for transferring coins between addresses
    def transfer_coins(self, sender, recipient, amount, fee):
        # Checking that the sender and recipient have the correct address format
        if len(sender) == 64 and len(recipient) == 64:
            # We check that the amount and commission are non-negative and do not exceed the maximum number of coins
            if 0 <= amount <= MAX_SUPPLY and 0 <= fee <= MAX_SUPPLY:
                # We check that the sender has sufficient funds for the transfer
                if self.get_balance(sender) >= amount + fee:
                    # Create a new transaction
                    transaction = Transaction(sender, recipient, amount, fee, None)
                    # Add it to the list of pending transactions
                    self.pending_transactions.append(transaction)
                    # Returning the transaction hash
                    return transaction.hash
                else:
                    # Return an error message if there are insufficient funds
                    return "Insufficient funds"
            else:
                # We return an error message if the amount or commission is incorrect
                return "Invalid amount or fee"
        else:
            # Return an error message if the addresses are incorrect
            return "Invalid sender or recipient address"

# Creating a Blockchain Instance
up_chain = Blockchain()
