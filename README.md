#CryptoPaymentsAPI

The **CryptoPaymentsAPI** class provides easy-to-use functionality for monitoring cryptocurrency transactions and fetching related information such as balances and transaction history. It offers flexibility for future expansion by allowing the addition of new blockchains dynamically.

**Examples of Usage:**

python
```
# Example 1: Convert amount for Bitcoin (BTC)
converted_amount = convert_amount(10000000, 'btc')
print("User-friendly amount for BTC:", converted_amount)  # Output: "0.1 BTC"

# Example 2: Fetch price for Ethereum (ETH)
price_eth = await getPrice('eth', 2.5)
print("Total value of 2.5 ETH in USD:", price_eth)  # Output: Total value in USD

# Example 3: Retrieve TON balance
balance_info = await getTonBalance("wallet_address")
print("TON balance:", balance_info['ton'])
print("Equivalent value in USD:", balance_info['usd'])

# Example 4: Retrieve last transactions for TON
transactions = await getTonLastTransactions("wallet_address")
print("Last transactions for TON:", transactions)

# Example 5: Monitor transactions for a specific user
monitoring_result = await monitorTransactions('user123', 'ton', 'wallet_address', '10000000', timeInterval=3600, memo='specific_memo')
print("Monitoring result:", monitoring_result)
```
**Error Handling:**

- Errors are handled to provide clear feedback and guidance for troubleshooting.
- Specific exceptions are raised with informative error messages to aid in debugging.
