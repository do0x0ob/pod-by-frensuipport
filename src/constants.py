import os
from pysui.sui.sui_constants import (
    DEVNET_SUI_URL,
    LOCALNET_SUI_URL,
    TESTNET_SUI_URL,
    MAINNET_SUI_URL,
    DEVNET_ENVIRONMENT_KEY,
    LOCALNET_ENVIRONMENT_KEY,
    TESTNET_ENVIRONMENT_KEY
)

# network enviroment mappping
NETWORK_ENV_MAP = {
    DEVNET_SUI_URL: DEVNET_ENVIRONMENT_KEY,
    LOCALNET_SUI_URL: LOCALNET_ENVIRONMENT_KEY,
    TESTNET_SUI_URL: TESTNET_ENVIRONMENT_KEY,
    MAINNET_SUI_URL: "mainnet"
}

# tasksheet type on testnet
#TASKSHEET_TYPE = "0xc8e76738b2a255fe5a093a39f1eaa3b3ab869efcd62e4705c8790ceb7a532f02::public_task::TaskSheet"

OBJECT_TYPE_ADDRESSES = {
    "TASKSHEET": {
        DEVNET_ENVIRONMENT_KEY: "0x_DEVNET_ADDRESS::public_task::TaskSheet",
        TESTNET_ENVIRONMENT_KEY: "0xc8e76738b2a255fe5a093a39f1eaa3b3ab869efcd62e4705c8790ceb7a532f02::public_task::TaskSheet",
        LOCALNET_ENVIRONMENT_KEY: "0x_LOCALNET_ADDRESS::public_task::TaskSheet",
        "mainnet": "0xYOUR_MAINNET_ADDRESS_HERE::public_task::TaskSheet"
    },
}

TASKS_FILE = os.path.join(os.path.dirname(__file__), 'tasks_cache.json')
