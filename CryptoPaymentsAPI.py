import aiohttp, asyncio, logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class scanAPI:
    def __init__(self):
        self.GetHeader = {"UserAgent" :"Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"}

    def convert_amount(self, amount: int, blockchain: str) -> str:
        """
        Converts an amount from the smallest unit to a user-friendly format for different blockchains.

        :param amount:
            The amount in the smallest unit (e.g., smallest unit of a cryptocurrency).
        :param blockchain:
            The blockchain type (e.g., 'btc', 'eth', 'bnb', 'sol') to determine the number of decimal places.

        :return:
            The amount converted to a user-friendly string with appropriate decimal places.

        :raises ValueError:
            If the blockchain type is not recognized.

        Example usage:
            amount = convert_to_user_friendly(10000000, 'btc')
            print(user_friendly_amount)  # Output: "0.1" for Bitcoin with 8 decimals
        """
        decimals_map = {
            'btc': 8,  # Bitcoin
            'eth': 18,  # Ethereum
            'bnb': 18,  # Binance Coin
            'sol': 9,  # Solana
            'ltc': 8,  # Litecoin
            'matic': 18,  # Polygon
            'ton': 9,  # The Open Network
            'doge': 8,  # Dogecoin
        }

        decimals = decimals_map.get(blockchain.lower())
        if decimals is None:
            raise ValueError(f"Unrecognized blockchain type: {blockchain}")

        if amount == 0:
            return "0"

        factor = 10 ** decimals
        user_friendly_amount = amount / factor

        return f"{user_friendly_amount:.{decimals}f}".rstrip('0').rstrip('.')

    async def getPrice(self, coin: str, amount: float | str) -> float:
        """
        Fetches the current market price of a specified cryptocurrency and calculates
        the total value for a given amount in USD.

        This function uses the CoinGecko API to retrieve the current price of the specified cryptocurrency.
        The price is then used to compute the total value of the given amount of the cryptocurrency in USD.

        Supported cryptocurrencies include:
        - BTC (Bitcoin)
        - ETH (Ethereum)
        - LTC (Litecoin)
        - BNB (Binance Coin)
        - SOL (Solana)
        - MATIC (Polygon)
        - TON (The Open Network)
        - DOGE (Dogecoin)

        :param coin:
            The symbol of the cryptocurrency to get the price for. Supported symbols are: 'btc', 'eth', 'ltc',
            'bnb', 'sol', 'matic', 'ton', 'doge'.
        :param amount:
            The amount of the cryptocurrency to calculate the value for. This can be provided as either a float or a string.
        :return:
            The total value of the specified amount of the cryptocurrency in USD, rounded to two decimal places.

        :raises ValueError:
            If the provided coin symbol is not supported or if the amount is not a valid number.
        :raises Exception:
            For any other errors such as network issues or API errors.

        Example usage:
            total_value = await getPrice('btc', 0.5)
            # This will return the total value of 0.5 BTC in USD.

            total_value = await getPrice('eth', '2.5')
            # This will return the total value of 2.5 ETH in USD.
        """
        url = 'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': 'bitcoin,ethereum,binancecoin,solana,litecoin,matic-network,the-open-network,dogecoin',
            'vs_currencies': 'usd'
        }

        valid_coins = {
            "btc": "bitcoin",
            "eth": "ethereum",
            "ltc": "litecoin",
            "bnb": "binancecoin",
            "sol": "solana",
            "matic": "matic-network",
            "ton": "the-open-network",
            "doge": "dogecoin"
        }

        coin = coin.lower()
        if coin not in valid_coins:
            raise ValueError(f"Unsupported coin symbol: {coin}. Supported symbols are: {', '.join(valid_coins.keys())}")

        try:
            amount = float(amount)
        except ValueError:
            raise ValueError("Amount must be a number.")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise Exception(f"Error fetching data from API: {response.status}")
                    response_data = await response.json()

            if valid_coins[coin] not in response_data:
                raise Exception(f"Data for {coin} not found in API response.")

            price_in_usd = response_data[valid_coins[coin]]['usd']
            total_value = round(price_in_usd * amount, 2)
            return total_value
        except Exception as ex:
            raise Exception(f"An error occurred: {str(ex)}")

    async def getTonBalance(self, address: str) -> dict:
        """
        Retrieves the TON (The Open Network) balance and its equivalent value in USD for a given wallet address.

        This function queries the TONCenter API to fetch wallet information for the specified address.
        It then calculates the TON balance, converts it to USD using the getPrice method, and returns the result.

        :param address:
            The wallet address for which the balance is to be retrieved.

        :return:
            A dictionary containing the TON balance and its equivalent value in USD.
            Example:
            {
                "ton": "123.45678",  # TON balance rounded to 5 decimal places
                "usd": 789.01          # Equivalent value in USD
            }

        :raises Exception:
            If there is any error during the API request or processing.
            The exception message will be printed for debugging purposes.

        Example usage:
            crypto_service = CryptoService()
            wallet_address = "ABCD123456789-1234567890abcdef"
            balance_info = await crypto_service.GetTonBalance(wallet_address)
            print(balance_info)
        """
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(f"https://toncenter.com/api/v2/getWalletInformation?address={address}",
                                             headers=self.GetHeader)
            response.raise_for_status()

            answer = await response.json()

            balance = self.convert_amount(amount = int(answer.get("result").get("balance")), blockchain= "ton")
            usd_value = await self.getPrice("ton", balance)

            return {"ton": balance, "usd": usd_value}
        except aiohttp.ClientResponseError as cre:
            print(f"HTTP error occurred: {cre.status} - {cre.message}")
            raise cre
        except aiohttp.ClientError as ce:
            print(f"Aiohttp client error occurred: {ce}")
            raise ce
        except Exception as ex:
            print(f"An error occurred while fetching TON balance: {ex}")
            raise ex

    async def getTonLastTransactions(self, address: str, limit: int = 20, offset: int = 0) -> list:
        """
        Retrieves the last transactions for a given TON (The Open Network) wallet address.

        This function queries the TONCenter API to fetch the most recent transactions for the specified wallet address.
        It processes the response to extract relevant information, including the transaction hash, timestamp, status,
        amount, and any associated memo.

        :param address:
            The wallet address for which the transactions are to be retrieved.
        :param limit:
            The maximum number of transactions to retrieve. Defaults to 20. Maximum 256 per 1 request.
        :param offset:
            The number of transactions to skip before starting to collect the result set. Defaults to 0.

        :return:
            A list of dictionaries, each containing details about a transaction.
            Example:
            [
                {
                    "address": "address1",
                    "hash": "transaction_hash",
                    "time": 1617181723,  # Unix timestamp
                    "success": True,
                    "amount": "1000000000",
                    "memo": "Transaction memo"
                },
                ...
            ]

        :raises Exception:
            If there is any error during the API request or processing.
            The exception message will be logged for debugging purposes.

        Example usage:
            CPA = CryptoPaymentsAPI()
            transactions = await CPA.getTonLastTransactions("wallet_address")
            print(transactions)
        """
        params = {
            'account': address,
            'limit': limit,
            'offset': offset
        }
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url="https://toncenter.com/api/v3/transactions",
                                             params=params)
                response.raise_for_status()
                data = await response.json()

            addresses = {}
            info = []

            for usrf in data.get('address_book', {}):
                addresses[usrf] = data['address_book'][usrf].get('user_friendly', "Unknown")

            for trx in data.get('transactions', []):
                memo = None
                if trx['in_msg']['message_content'].get('decoded') and trx['in_msg']['message_content']['decoded'].get(
                        "comment"):
                    memo = trx['in_msg']['message_content']['decoded']['comment']

                try:
                    info.append(
                        {
                            "address": addresses.get(trx['in_msg'].get('source'), "Unknown address"),
                            "hash": trx['hash'],
                            "time": trx['now'],
                            "success": trx['description']['compute_ph'].get('success', False),
                            "amount": self.convert_amount(amount = int(trx['in_msg'].get('value')), blockchain= "ton"),
                            "memo": memo
                        }
                    )
                except KeyError as e:
                    logger.warning(f"KeyError while processing transaction: {e}")

            return info
        except aiohttp.ClientResponseError as cre:
            logger.error(f"HTTP error occurred: {cre.status} - {cre.message}")
        except aiohttp.ClientError as ce:
            logger.error(f"Aiohttp client error occurred: {ce}")
        except Exception as ex:
            logger.error(f"An error occurred while fetching transactions: {ex}")

        return []

class CryptoPaymentsAPI(scanAPI):
    def __init__(self):
        super().__init__()
        self.stop_events = defaultdict(asyncio.Event)

    async def stop_monitoring(self, user_id: str):
        """
        Sets the stop event for a specific user, indicating to stop monitoring transactions for that user.
        """
        self.stop_events[user_id].set()

    async def monitorTransactions(self, user_id: any, blockchain: str, address: str, amount: str, timeInterval: int = 3600, memo: str = None, checkTime: int = 5) -> bool:
        """
        Monitors transactions on a specified blockchain for a given address, amount, and optional memo for a specific user.

        This function continuously checks for new transactions on the specified blockchain for a given address and user.
        It compares each transaction's amount and, optionally, memo with the specified criteria.
        If a transaction matching the criteria is found, the function returns True.
        The monitoring process stops if the specified time interval elapses or if the stop event is set for the user.

        :param user_id:
            The unique identifier of the user who initiated the monitoring.
        :param blockchain:
            The blockchain to monitor transactions on. Supported values are 'ton' (The Open Network) and other blockchains
            which can be added dynamically.
        :param address:
            The wallet address to monitor for transactions.
        :param amount:
            The amount of cryptocurrency to monitor for in the transactions.
        :param timeInterval:
            The time interval (in seconds) for which to monitor transactions. Default is 3600 seconds (1 hour).
        :param memo:
            Optional. The memo associated with the transactions to monitor. Default is None.
        :param checkTime:
            The time interval (in seconds) between checks for new transactions. Default is 5 seconds.

        :return:
            True if a transaction matching the criteria is found within the specified time interval, False otherwise.

        :raises ValueError:
            If an unsupported blockchain type is provided.

        :raises Exception:
            If there is an error during the monitoring process.

        Example usage:
            CPA = CryptoPaymentsAPI()
            monitoring_result = await CPA.monitorTransactions('user123', 'ton', 'wallet_address', '10000000', memo='specific_memo')
            print("Monitoring result:", monitoring_result)
        """
        self.stop_events[user_id].clear()
        try:
            i = 0
            while i <= timeInterval:
                if self.stop_events[user_id].is_set():
                    return False
                if blockchain == "ton":
                    transactions = await self.getTonLastTransactions(address)
                    for trx in transactions:
                        if trx['amount'] == amount and (memo is None or trx['memo'] == memo):
                            return True
                    await asyncio.sleep(checkTime)
                    i += checkTime
                else:
                    raise ValueError(f"Unsupported blockchain type: {blockchain}")
        except ValueError as ve:
            print(f"ValueError: {ve}")
            raise
        except Exception as ex:
            print(f"An error occurred during monitoring: {ex}")
            raise
        return False

