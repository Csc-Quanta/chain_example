# Copyright 2021 yijiachen
# 
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import time
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from base.Base import BlockchainClient

HOSTS = ['113.31.103.193',
         '113.31.105.244',
         '113.31.107.126', # address for Node 1, used for test below
         '113.31.144.146',
         '113.31.144.63',
         '113.31.102.169']
ALICE_ADDR = '1c22a1fd483c60d68485c4b6b6295aa3135d2dcc'
ALICE_PK = '70ba4fd2cf9d596169a9adb11b583e9e20660c35ad5cecb62ea6d3653ec0eea2'

def test1_all_success():
    """
    All successful operations in a series.
    """

    client = BlockchainClient(host='http://'+HOSTS[2])

    # create new account
    addr, pk = client._new_key() # TODO should be named created account
    balance = client._get_account_balance(addr)
    assert(balance == 0)

    # perform a transaction from an existing account
    alice_balance = client._get_account_balance(ALICE_ADDR)
    tx_amount = 500
    tx_hash = client._tx(ALICE_ADDR, ALICE_PK, addr, tx_amount)
    check_transaction(client, tx_hash, 'PAYMENR')

    # verify balance of both parties after transaction
    alice_new_balance = client._get_account_balance(ALICE_ADDR)
    new_balance = client._get_account_balance(addr)
    assert(alice_balance - tx_amount == alice_new_balance)
    assert(balance + tx_amount == new_balance)

    print('test passed!')

    # # create and trade dogecoin token (FIXME currently timeout)
    # tx_hash = client._create_token(addr, pk, 'DOGE', 54526238799)
    # check_transaction(client, tx_hash, 'CREATE_DOGE')
    # tx_hash = client._tx_token(addr, pk, 'DOGE', 5000, 2500, [addr, ALICE_ADDR])
    # check_transaction(client, tx_hash, 'TRADE_DOGE')

    # # create and call smart contract (FIXME currently timeout)
    # tx_hash, contract_hash = client._create_contract(addr, pk, '1b')
    # check_transaction(client, tx_hash, 'CREATE_CONTRACT', wait_ms=60000)
    # tx_hash = client._call_contract(addr, pk, contract_hash, '1b')
    # check_transaction(client, tx_hash, 'CALL_CONTRACT')

def test2_partial_success():
    """
    TODO test some unsuccessful scenarios:
     - negative balance transactions
     - nonexistent tokens and smart contracts
     - violations of smart contracts
     - etc.
    """
    return

def check_transaction(client, tx_hash, tx_name='', wait_ms=10000):
    if tx_name:
        print('\nchecking transaction', tx_name)

    # immediately check whether transaction is successful
    is_success, _ = client._check_tx_ex(tx_hash)
    print('transaction is', 'successful' if is_success else 'pending')

    # wait and check again
    is_success, _, time = client._check_tx_wait_ex(tx_hash, _waitms=wait_ms)
    try:
        assert(is_success)
    except:
        raise TimeoutError("wow")
    print('transaction is successful after', time, 'ms')