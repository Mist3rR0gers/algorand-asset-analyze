import requests
from requests.utils import requote_uri
import json
import sys
from datetime import datetime, timedelta, timezone
#python asset_analyze.py <asset-id> 
args = sys.argv[1:]
asset_list = []
funder_asset_list = []
funder_list = []
receiver_asset_list = []
d = datetime.now(timezone.utc).astimezone() - timedelta(days=7)

id = requests.get('https://algoexplorerapi.io/idx2/v2/assets?asset-id=' + str(args[0]))
id_response = json.loads(id.text)
balances = requests.get('https://algoexplorerapi.io/idx2/v2/assets/' + str(args[0]) + '/balances')
balance_response = json.loads(balances.text)
try:
    creator = id_response['assets'][0]['params']['creator']
    total = id_response['assets'][0]['params']['total']
    for balance in balance_response['balances']:
        if balance['address'] == creator:
            creator_balance=int(balance['amount'])
        else:
            creator_balance=0
    assets = requests.get('https://algoexplorerapi.io/idx2/v2/assets?creator=' + creator)
    assets_response = json.loads(assets.text)
    for asset in assets_response['assets']:
        asset_list.append(asset['params']['name'])
    transactions = requests.get(requote_uri('https://algoexplorerapi.io/idx2/v2/accounts/' + creator + '/transactions?after-time=' + str(d.isoformat()) + '&tx-type=pay'))
    transaction_response = json.loads(transactions.text)
    for transaction in transaction_response['transactions']:
        if transaction['sender'] != creator:
            senders = requests.get('https://algoexplorerapi.io/idx2/v2/assets?creator=' + transaction['sender'])
            sender_response = json.loads(senders.text)
            if transaction['sender'] not in funder_list:
                funder_list.append(transaction['sender'])
                for sender in sender_response['assets']:
                    if sender['params']['name'] not in funder_asset_list:
                        funder_asset_list.append(sender['params']['name'])
    for funder in funder_list:
        transactions = requests.get(requote_uri('https://algoexplorerapi.io/idx2/v2/accounts/' + str(funder) + '/transactions?after-time=' + str(d.isoformat()) + '&tx-type=pay'))
        transaction_response = json.loads(transactions.text)
        for transaction in transaction_response['transactions']:
            if transaction['payment-transaction']['receiver'] != funder:
                receivers = requests.get('https://algoexplorerapi.io/idx2/v2/assets?creator=' + transaction['payment-transaction']['receiver'])
                receiver_response = json.loads(receivers.text)
                for receiver in receiver_response['assets']:
                    if sender['params']['name'] not in receiver_asset_list:
                        receiver_asset_list.append(sender['params']['name'])
except:
    pass

print('The creator wallet owns ' + str(creator_balance) + ' of the asset.')
print('The creator wallet has minted the following: ' + str(asset_list))
print('Assets created by funding wallets: ' + str(funder_asset_list)) 
print('Assets created by wallets funded by funding wallet: ' + str(receiver_asset_list))
print('Wallets that have funded creator wallet in the last 7 days: ' + str(funder_list))
