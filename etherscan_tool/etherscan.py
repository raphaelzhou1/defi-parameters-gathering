import json
from importlib import resources
from json import tool

import requests

import modules.modules as aggregate_modules

import configs
from enums.enums import FieldsEnum as fields

class Etherscan:
    def __new__(cls, api_key: str, net: str = "MAINNET"):
        with resources.path(configs, f"{net.upper()}.json") as path: # path object
            config_path = str(path) # i.e., /Users/tianyu/Desktop/Blockchain Programs/tianyu-defi-parameters-gathering/etherscan_tool/configs/MAINNET.json
        return cls.from_config(api_key=api_key, config_path=config_path, net=net)

    @staticmethod
    def __load_config(config_path: str) -> dict:
        with open(config_path, "r") as f: # reads and creates a File Object
            return json.load(f) # converts File to JSON object

    @staticmethod
    def __run(func, api_key: str, net: str):
        def wrapper(*args, **kwargs):
            url = (
                f"{fields.PREFIX.format(net.lower()).replace('-main','')}"
                f"{func(*args, **kwargs)}"
                f"{fields.API_KEY}"
                f"{api_key}"
            )
            r = requests.get(url, headers={"User-Agent": ""}) # returns a requests.Response object
            return parser.parse(r)
        return wrapper

    @classmethod
    def from_config(cls, api_key: str, config_path: str, net: str):
        config = cls.__load_config(config_path) # returns JSON object (a dictionary)
        for func, v in config.items(): # each pair in the Dict
            if not func.startswith("_"):  # disabled if _
                attr = getattr(getattr(aggregate_modules, v["module"].capitalize()), func) # aggregate_modules refers to file modules of folder modules; v["module"] returns particular class name in aggregate_modules; func is the static function that should be returned as a function
                setattr(cls, func, cls.__run(attr, api_key, net))
        return cls

class ResponseParser:
    @staticmethod
    def parse(response: requests.Response):
        content = response.json()
        result = content["result"]
        if "status" in content.keys():
            status = bool(int(content["status"]))
            message = content["message"]
            assert status, f"{result} -- {message}"
        else:
            # GETH or Parity proxy msg format
            # TODO: see if we need those values
            jsonrpc = content["jsonrpc"]
            cid = int(content["id"])
        return result

def main():
    etherscan = Etherscan("TE9HIXVD4MTIGAP9SJB8F3V4E39UTP8C1E")
    print(etherscan.get_eth_balance("TE9HIXVD4MTIGAP9SJB8F3V4E39UTP8C1E"))

# print(test_run("<function Proxy.get_proxy_block_number at 0x105f1e560>", "TE9HIXVD4MTIGAP9SJB8F3V4E39UTP8C1E", "MAINNET"))
main()