from pysui import SuiConfig, SyncClient
import os

# 直接從 sui_constants 導入需要的常量
from pysui.sui.sui_constants import (
    PYSUI_CLIENT_CONFIG_ENV,
    DEVNET_SUI_URL,
    LOCALNET_SUI_URL,
    TESTNET_SUI_URL,
    MAINNET_SUI_URL,
    DEVNET_ENVIRONMENT_KEY,
    LOCALNET_ENVIRONMENT_KEY,
    TESTNET_ENVIRONMENT_KEY
)

# 創建 URL 到環境名稱的映射
NETWORK_ENV_MAP = {
    DEVNET_SUI_URL: DEVNET_ENVIRONMENT_KEY,
    LOCALNET_SUI_URL: LOCALNET_ENVIRONMENT_KEY,
    TESTNET_SUI_URL: TESTNET_ENVIRONMENT_KEY,
    MAINNET_SUI_URL: "mainnet"
}

def sui_addresses(client: SyncClient) -> None:
    """Print all addresses."""
    _all_add: list = client.config.addresses
    _aliases = client.config.aliases
    cur_url = client.config.rpc_url

    # 獲取當前網絡環境名稱
    current_env = NETWORK_ENV_MAP.get(cur_url, "unknown").upper()

    #print(f"current network url is: {cur_url}")
    print(f"current network environment: {current_env}")
    #print(f"all addresses are : {all_add}")
    #print(f"active address: {client.config.active_address}")
    #print(f"aliases: {aliases}, type: {type(aliases)}")

def main():
    cfg = SuiConfig.default_config()
    print(f"Using configuration from {os.environ.get(PYSUI_CLIENT_CONFIG_ENV, 'default location')}")

    client = SyncClient(cfg)
    sui_addresses(client)

if __name__ == "__main__":
    main()