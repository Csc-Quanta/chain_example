import json
import logging
import time
import os
import sys
import requests
from geventhttpclient import HTTPClient, URL

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from config import settings, application

logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)


class BlockchainClient(object):
    """
    区块链测试客户端
    """
    host = 'http://113.31.107.126' # temporary
    port = '38000'
    headers = {"Content-Type": "application/json"}

    def __init__(self, host='http://113.31.107.126', port='38000', concurrency=application.data['locust']['concurrency']):
        self.host = host
        self.port = port
        self.url = URL(self.host + ':' + self.port)
        self.req = HTTPClient.from_url(self.url, concurrency=concurrency)

        self._dict = {
            'tx': self._tx,
            'newkey': self._new_key,
            'create_contract': self._create_contract,
            'call_contract': self._call_contract,
            'create_token': self._create_token,
            'mint_token': self._mint_token,
            'burn_token': self._burn_token,
            'tx_token': self._tx_token,
            'check_tx': self._check_tx,
            'check_tx_wait': self._check_tx_wait,
            'check_tx_ex': self._check_tx_ex,
            'check_tx_wait_ex': self._check_tx_wait_ex,
            'check_call_contract': self._check_call_contract,
            'get_account': self._get_account,
            'get_account_balance': self._get_account_balance,
            'get_account_nonce': self._get_account_nonce,
            'get_account_token': self._get_account_token
        }
        # self.req = requests.Session()

    def __getattr__(self, name):
        return self._dict[name]

    def __post(self, target, data):
        j = json.dumps(data)
        response = self.req.post(request_uri=target, body=j, headers=self.headers)
        if response.status_code == 200:
            result = json.loads(response.read())
            if result['rplCode'] >= 0:
                # tx = result['txHash']
                return result
            else:
                err = RuntimeError(f"error.code={result['rplCode']}, msg={result['rplMsg']}")
                raise err
        else:
            err = RuntimeError(f"remote http error, status={response.status_code}, result={response.get('location')}")
            raise err

    def _new_key(self):
        response = self.req.get(request_uri=settings.CONST_NEW_KEY)
        if response.status_code == 200:
            result = json.loads(response.read())
            if result['rplCode'] >= 0:
                return result['address'], result['priKey']
            else:
                err = RuntimeError(f"error.code={result['rplCode']}, msg={result['rplMsg']}")
                raise err
        else:
            err = RuntimeError(f"remote http error, status={response.status_code}, result={response.content}")
            raise err

    def _tx(self, _from, _pk, _to, _amount, _from_slice=-1, _to_slice=-1):
        """
        主链币交易。
        :param _from: 转出账户地址
        :param _pk: 转出账户私钥
        :param _to: 转入账户地址
        :param _amount: 交易金额
        :return: 交易hash
        """
        data = {
            "from": _from,
            "fromSlice": _from_slice,
            "amount": _amount,
            "priKey": _pk,
            "tos": [{
                "address": _to,
                "slice": _to_slice,
                "amount": _amount
            }]
        }
        result = self.__post(settings.CONST_TX, data)
        return result['txHash']

    def _create_contract(self, _from, _pk, _code, _from_slice=1):
        """
        创建合约
        :param _from: 创建账户地址
        :param _pk: 创建账户私钥
        :param _code: 合约代码，HEX格式字符串
        :param _from_slice: 分片，默认-1
        :return: 交易hash, 合约地址
        """
        data = {
            "address": _from,
            "slice": _from_slice,
            "priKey": _pk,
            "code": _code
        }
        result = self.__post(settings.CONST_CREATE_CONTRACT, data)
        return result['txHash'], result['contractHash']

    def _call_contract(self, _from, _pk, _contract, _function, _param_define=[], _params=[], _from_slice=-1):
        """
        调用合约
        :param _from: 创建账户地址
        :param _pk: 创建账户私钥
        :param _contract: 合约地址
        :param _function: 函数名称
        :param _param_define: 参数定义,默认为[]. eg: ["uint256", "address"]
        :param _params: 调用参数,默认为[]. eg: [{"value":20, "type":"long"}, {"value":"xxxxxx", "type":"string"}]
        :param _from_slice: 分片号，默认-1
        :return: 交易hash
        """
        # target = self.host+_BC_CALL_CONTRACT
        data = {
            "address": _from,
            "slice": _from_slice,
            "priKey": _pk,
            "contractAddress": _contract,
            "function": {
                "name": _function,
                "params": _param_define
            },
            "params": _params
        }
        result = self.__post(settings.CONST_CALL_CONTRACT, data)
        return result['txHash']

    def _create_token(self, _from, _pk, _token, _amount):
        """
        创建20Token
        :param _from: 创建账户地址
        :param _pk: 创建账户私钥
        :param _token: token名称
        :param _amount: token数量
        :return: 交易hash
        """
        # target = self.host+_BC_CREATE_TOKEN
        data = {
            "address": _from,
            "priKey": _pk,
            "token": _token,
            "amount": _amount
        }
        result = self.__post(settings.CONST_CREATE_TOKEN, data)
        return result['txHash']

    def _mint_token(self, _from, _pk, _token, _amount):
        """
        增发20Token
        :param _from: 创建账户地址
        :param _pk: 创建账户私钥
        :param _code: 合约代码，HEX格式字符串
        :param _token: token名称
        :param _amount: 增发数量
        :return: 交易hash
        """
        # target = self.host+_BC_MINT_TOKEN
        data = {
            "address": _from,
            "priKey": _pk,
            "token": _token,
            "amount": _amount
        }
        result = self.__post(settings.CONST_MINT_TOKEN, data)
        return result['txHash']

    def _burn_token(self, _from, _pk, _token, _amount):
        """
        销毁20Token
        :param _from: 创建账户地址
        :param _pk: 创建账户私钥
        :param _code: 合约代码，HEX格式字符串
        :param _token: token名称
        :param _amount: 销毁数量
        :return: 交易hash
        """
        # target = self.host+_BC_MINT_TOKEN
        data = {
            "address": _from,
            "priKey": _pk,
            "token": _token,
            "amount": _amount
        }
        result = self.__post(settings.CONST_BURN_TOKEN, data)
        return result['txHash']

    def _tx_token(self, _from, _pk, _token, _from_amount, _to_amount, _to=[], _from_slice=-1, _to_slice=-1):
        """
        交易20Token
        :param _from: 创建账户地址
        :param _pk: 创建账户私钥
        :param _code: 合约代码，HEX格式字符串
        :param _token: token名称
        :param _amount: 交易数量
        :return: 交易hash
        """
        tos_list = []
        for i in _to:
            to_data = {
                "address": i,
                "slice": _to_slice,
                "amount": _to_amount
            }
            tos_list.append(to_data)
        data = {
            "from": _from,
            "fromSlice": _from_slice,
            "priKey": _pk,
            "token": _token,
            "amount": _from_amount,
            "tos": tos_list
        }
        result = self.__post(settings.CONST_TX_TOKEN, data)
        return result['txHash']

    def _check_tx_ex(self, _tx):
        """
        立即检查交易结果
        :param _tx: 交易hash
        :return: 是否成功, 交易详情
        """
        data = {
            "hash": _tx
        }
        j = json.dumps(data)
        response = self.req.post(request_uri=settings.CONST_GET_TX_BY_HASH, body=j, headers=self.headers)
        if response.status_code == 200:
            result = json.loads(response.read())
            if result['retCode'] >= 0:
                t = result['transaction']
                r = t.get('status') == 'D'
                return r, t
            else:
                return False, {}
        else:
            raise RuntimeError(f"remote http error, status={response.status_code}, result={response.content}")

    def _check_tx_wait_ex(self, _tx, _waitms=10000):
        """
        检查交易结果，如果交易不成功在等待
        :param _tx: 交易hash
        :param _waitms: ，如果交易成功则立即返回，否则等待的毫秒数
        :return: 是否成功, 交易详情
        """
        _counter = _waitms

        r, t = self._check_tx_ex(_tx)
        while _counter > 0 and not r:
            time.sleep(0.1)
            _counter = _counter - 100
            r, t = self._check_tx_ex(_tx)
        return r, t, _waitms - _counter

    def _check_tx(self, _tx):
        """
        立即检查交易结果
        :param _tx: 交易hash
        :return: 是否成功
        """
        r, t = self._check_tx_ex(_tx)
        return r

    def _check_tx_wait(self, _tx, _waitms=10000):
        """
        检查交易结果，如果交易不成功在等待
        :param _tx: 交易hash
        :param _waitms: ，如果交易成功则立即返回，否则等待的毫秒数
        :return: 是否成功
        """
        r, t = self._check_tx_wait_ex(_tx, _waitms)
        return r

    def _check_call_contract(self, _tx, _waitms=10000):
        """
        检查合约调用结果
        :param _tx: 交易hash
        :param _waitms: ，如果交易成功则立即返回，否则等待的毫秒数
        :return: 是否成功, 调用数据, 合约返回值

        """
        r, t = self._check_tx_wait_ex(_tx, _waitms)
        return r, t['txBody']['data'], t['result']

    def _get_account(self, _addr):
        """
        查询账户信息
        :param _addr: 账户地址
        :return: 账户
        """
        data = {
            "address": _addr,
        }
        j = json.dumps(data)
        response = self.req.post(request_uri=settings.CONST_GET_ADDR, body=j, headers=self.headers)
        if response.status_code == 200:
            result = json.loads(response.read())
            if result['retCode'] >= 0:
                acct = result['account']
                return acct
            else:
                err = RuntimeError(f"error.code={result['rplCode']}, msg={result['rplMsg']}")
                raise err
        else:
            err = RuntimeError(f"remote http error, status={response.status_code}, result={response.content}")
            raise err

    def _get_account_balance(self, _addr):
        acct = self._get_account(_addr)
        if acct and acct.get('balance'):
            return int(acct['balance'])
        else:
            return 0

    def _get_account_nonce(self, _addr):
        acct = self._get_account(_addr)
        if acct and acct.get('nonce'):
            return acct['nonce']
        else:
            return 0

    def _get_account_token(self, _addr, _token):
        acct = self._get_account(_addr)
        if acct and acct.get('tokens'):
            for t in acct['tokens']:
                if t and t['token'] == _token:
                    return int(t['balance'][:-18])
            return 0
        else:
            return 0


class InterFaceRequests(object):

    def load_basic_variabeles_json(self):
        """
        加载基础环境参数
        :return: basic_params
        """
        with open("files/basic_variables.json", "r", encoding="utf-8") as f:
            basic_params = json.load(f)
            # print(basic_params)
        return basic_params

    def post_method(self, ip_port, api_path, data):
        """
        发送post请求的简单封装。
        :param ip_port: 请求的ip和端口号
        :param api_path: 请求接口路径
        :param data: 请求的数据
        :return: 接口请求返回的content数据
        """
        url = ip_port + api_path
        try:
            res = requests.post(url=url, json=data)
            if res.status_code == 200:
                response = res.content
                return response
        except Exception as e:
            log.error(f"报错信息：{e}")
            return e

    def format_data(self, data):
        """
        格式化json数据的显示形式。
        :param data: 需要格式化的内容
        :return: 格式化后的数据
        """
        if isinstance(data, dict):
            my_data = json.dumps(data,
                                 ensure_ascii=False,
                                 sort_keys=True,
                                 indent=4,
                                 separators=(',', ':'))
        else:
            my_data = json.dumps(eval(data),
                                 ensure_ascii=False,
                                 sort_keys=True,
                                 indent=4,
                                 separators=(',', ':'))
        return my_data

    def address_new_keys(self, ip_port, api_path):
        """
        获取秘钥对接口。
        :param ip_port: 请求ip和端口号
        :param api_path: 请求地址
        :return: 字典格式的返回数据
        """
        url = ip_port + api_path
        log.info(f"获取秘钥对地址：{url}")
        data = ""
        res = self.post_method(ip_port=ip_port, api_path=api_path, data=data)
        # result = self.format_data(data=res)
        # log.info(f"\n获取秘钥对返回：\n{result}\n")
        response = eval(res)
        address = response.get('address')
        prikey = response.get('priKey')
        return address, prikey

    def transaction(self, ip_port, api_path, from_address, from_Slice, from_amount, from_priKey, *to_address_items):
        """
        主币交易接口。
        :param ip_port: 请求ip和端口号
        :param api_path: 请求路径
        :param from_address: 转出地址
        :param from_Slice: 转出地址所在分片
        :param from_amount: 转出金额
        :param from_priKey: 转出地址私钥
        :param to_address_items:  对应转入地址的：address, slice, amount
        :return: 交易hash
        """
        url = ip_port + api_path
        log.info(f"主币交易地址：{url}")

        output_list = []
        if len(to_address_items) % 3 == 0 and len(to_address_items) != 0:
            n = 3
            data_list = [to_address_items[i:i + n] for i in range(0, len(to_address_items), n)]
            # print(data_list)
            for j in data_list:
                output = {
                    "address": j[0],
                    "slice": j[1],
                    "amount": j[2]
                }
                output_list.append(output)
            # 拼接请求数据字典
            data = {
                "from": from_address,
                "fromSlice": from_Slice,
                "amount": from_amount,
                "priKey": from_priKey,
                "tos": output_list
            }
            req_result = self.format_data(data=data)
            log.info(f"主币交易请求：\n{req_result}")
            # 发送请求数据
            res = self.post_method(ip_port=ip_port, api_path=api_path, data=data)
            result = self.format_data(data=res)
            log.info(f"主币交易返回：\n{result}")
            tx_hash = eval(res).get('txHash')
            return tx_hash
        else:
            log.error("参数对不匹配 ！")

    def token20_TX(self, ip_port, api_path, from_address, from_Slice, from_amount, from_priKey, token_name,
                   *to_address_items):
        """
        发起token20交易
        :param ip_port: 请求ip和端口号
        :param api_path: 请求路径
        :param from_address: 转出地址
        :param from_Slice: 转出地址所在的分片
        :param from_amount: 转出金额
        :param from_priKey: 转出地址对应私钥
        :param token_name: token名称
        :param to_address_items: 转入账户对应的address, slice, amount
        :return: 交易hash
        """
        url = ip_port + api_path
        log.info(f"token交易地址：{url}")

        output_list = []
        if len(to_address_items) % 3 == 0 and len(to_address_items) != 0:
            n = 3
            data_list = [to_address_items[i:i + n] for i in range(0, len(to_address_items), n)]
            # print(data_list)
            for j in data_list:
                output = {
                    "address": j[0],
                    "slice": j[1],
                    "amount": j[2]
                }
                output_list.append(output)
            # 拼接请求数据字典
            data = {
                "from": from_address,
                "fromSlice": from_Slice,  # 1-254 有效
                "amount": from_amount,
                "token": token_name,
                "priKey": from_priKey,
                "tos": output_list
            }
            req_result = self.format_data(data)
            log.info(f"token交易请求：\n{req_result}")
            # 发送请求数据
            res = self.post_method(ip_port=ip_port, api_path=api_path, data=data)
            result = self.format_data(res)
            log.info(f"token交易返回：\n{result}")
            tx_hash = eval(res).get('txHash')
            return tx_hash
        else:
            log.error("参数对不匹配！")

    def get_transaction_info_by_TXhash(self, ip_port, api_path, tx_hash):
        """
        根据交易hash查询交易信息
        :param ip_port: 请ip和端口
        :param api_path: 接口地址
        :param tx_hash: 交易hash
        :return: 返回交易详情
        """
        url = ip_port + api_path
        log.info(f"根据交易hash查询交易信息地址：{url}")
        data = {"hash": tx_hash}
        log.info(f"根据交易hash查询交易请求：\n{data}")
        log.info("等待交易入块···")
        n = 0
        while True:
            res = self.post_method(ip_port=ip_port, api_path=api_path, data=data)
            # print(res)
            n += 1
            print(n, "···")
            if n >= 30:
                log.info("交易入块超时")
                break
            if eval(res).get('transaction').get('status') == 'D':
                break
            time.sleep(1)
        log.info("交易入块成功！")
        result = self.format_data(data=res)
        log.info(f"获取秘钥对返回：\n{result}")
        response = eval(res)
        return response, n

    def get_account_info_by_address(self, ip_port, api_path, address):
        """
        根据账户地址查询账户信息
        :param ip_port: ip和端口
        :param api_path: 接口地址
        :param address: 账户地址
        :return: 账户详情
        """
        url = ip_port + api_path
        log.info(f"查询账户信息地址：{url}")
        data = {"address": address}
        log.info(f"查询账户请求：\n{data}")
        res = self.post_method(ip_port=ip_port, api_path=api_path, data=data)
        result = self.format_data(data=res)
        log.info(f"查询账户信息返回：\n{result}")
        response = eval(res)
        return response

    def create_token_20(self, ip_port, api_path, token_name, amount, address, priKey, address_slice):
        """
        创建token20代币
        :param ip_port: ip和端口号
        :param api_path: 接口路径
        :param token_name: 代币名称
        :param amount: 创建时原始金额
        :param address: 代币所在的账户地址
        :param priKey: 账户地址对应的私钥
        :param address_slice: 所在分片
        :return: 返回创建token20的结果
        """
        url = ip_port + api_path
        log.info(f"创建token20请求地址：{url}")
        data = {
            "token": token_name,
            "amount": amount,
            "address": address,
            "priKey": priKey,
            "slice": address_slice
        }
        result_1 = self.format_data(data=data)
        log.info(f"创建token20请求数据：\n{result_1}")
        rep = self.post_method(ip_port=ip_port, api_path=api_path, data=data)
        result_2 = self.format_data(data=rep)
        log.info(f"创建token20返回数据：\n{result_2}")
        response = eval(rep)
        return response

    def add_token(self, ip_port, api_path, token_name, token_amount, address, address_prikey, address_slice):
        """
        token增发，规则：只针对token20，只对应的token20余额会产生变化，token20所在的账户地址余额不变
        :param ip_port: ip和端口
        :param api_path: 接口地址
        :param token_name: 代币名称
        :param token_amount: 增发数量
        :param address: 代币所在的地址
        :param address_prikey: 地址对应的秘钥
        :param address_slice: 账户所在分片
        :return: token20增加返回结果
        """
        url = ip_port + api_path
        log.info(f"增发token地址：{url}")
        data = {
            "token": token_name,
            "amount": token_amount,
            "address": address,
            "priKey": address_prikey,
            "slice": address_slice
        }
        json_data = self.format_data(data)
        log.info(f"增发token请求：\n{json_data}")
        res = self.post_method(ip_port=ip_port, api_path=api_path, data=data)
        result = self.format_data(res)
        log.info(f"增发token返回：\n{result}")
        response = eval(res)
        return response

    def get_new_block_info(self, ip_port, api_path):
        """
        获取最新区块信息
        :param ip_port: ip和端口
        :param api_path: 接口地址
        :return: 最新区块信息
        """
        url = ip_port + api_path
        log.info(f"获取最新区块地址：{url}")
        data = ""
        res = self.post_method(ip_port=ip_port, api_path=api_path, data=data)
        result = self.format_data(res)
        log.info(f"获取最新区块返回：\n{result}")
        response = eval(res)
        return response

    def destroy_token(self, ip_port, api_path, token_name, token_amount, address, address_prikey, address_slice):
        """
        token销毁，销毁的意思是，将账户余额一直减少，最少到0为止
        :param ip_port: ip和端口
        :param api_path: 接口路径
        :param token_name: token名称
        :param token_amount: 销毁金额
        :param address: 销毁账户所在的地址
        :param address_prikey: 地址对应的私钥
        :param address_slice: 地址所在的分片
        :return: 返回销毁结果
        """
        url = ip_port + api_path
        log.info(f"token销毁地址：{url}")
        data = {
            "token": token_name,
            "amount": token_amount,
            "address": address,
            "priKey": address_prikey,
            "slice": address_slice
        }
        json_data = self.format_data(data)
        log.info(f"token销毁请求：\n{json_data}")
        res = self.post_method(ip_port=ip_port, api_path=api_path, data=data)
        result = self.format_data(res)
        log.info(f"token销毁返回：\n{result}")
        response = eval(res)
        return response

    def create_token_721(self, ip_port, api_path, address, address_prikey, address_slice, symbol_name, tolal,
                         tokens_items_list):
        """
        创建token721
        :param ip_port: ip和端口
        :param api_path: 接口地址
        :param address: 地址
        :param address_prikey: 地址对应的私钥
        :param address_slice: 地址所在的分片
        :param symbol_name: token721 名称
        :param tolal: token721数量
        :param tokens_items: 对应token721的name 和 code字段
        :return: 返回创建token721结果
        """

        url = ip_port + api_path
        log.info(f"创建token721地址：{url}")

        # tokens_items_list = []
        if len(tokens_items_list) == tolal:
            data = {
                "address": address,
                "priKey": address_prikey,
                "slice": address_slice,
                "cryptoToken": {
                    "symbol": symbol_name,
                    "total": tolal,
                    "tokens": tokens_items_list
                }
            }
            req_result = self.format_data(data)
            log.info(f"创建token721请求数据：\n{req_result}")
            # 发送创建token721请求
            res = self.post_method(ip_port=ip_port, api_path=api_path, data=data)
            result = self.format_data(res)
            log.info(f"创建token721返回：\n{result}")
            response = eval(res)
            return response
        else:
            log.error("参数对不匹配 ！")

    def token_721_TX(self, ip_port, api_path, from_address, from_slice, from_address_prikey, symbol_name, tokenHash,
                     to_address, to_slice):
        """
        token721交易
        :param ip_port: ip、端口
        :param api_path: 接口地址
        :param from_address: 账户地址
        :param from_slice: 账户所在分片
        :param from_address_prikey: 地址对应的分片
        :param symbol_name: token721 名称
        :param tokenHash: 查询账户信息时得到token721的hash
        :param to_address: 转入账户地址
        :param to_slice: 转入账户所在的分片
        :return: 返回交易结果信息
        """
        url = ip_port + api_path
        log.info(f"token721交易地址：{url}")
        data = {
            "from": from_address,
            "fromSlice": from_slice,
            "priKey": from_address_prikey,
            "symbol": symbol_name,
            "tokenHash": tokenHash,
            "tos": [
                {
                    "address": to_address,
                    "slice": to_slice
                }
            ]
        }
        req_result = self.format_data(data)
        log.info(f"token721交易请求：\n{req_result}")
        # 发送创建token721请求
        res = self.post_method(ip_port=ip_port, api_path=api_path, data=data)
        result = self.format_data(res)
        log.info(f"token721交易返回：\n{result}")
        response = eval(res)
        return response
