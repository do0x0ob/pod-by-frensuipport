from typing import Optional
from pysui import SuiConfig, SyncClient, AsyncClient
from pysui.sui.sui_types.address import SuiAddress
from pysui.sui.sui_builders.get_builders import GetObjectsOwnedByAddress
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
import os
import asyncio
import warnings
import json
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 創建 URL 到環境名稱的映射
NETWORK_ENV_MAP = {
    DEVNET_SUI_URL: DEVNET_ENVIRONMENT_KEY,
    LOCALNET_SUI_URL: LOCALNET_ENVIRONMENT_KEY,
    TESTNET_SUI_URL: TESTNET_ENVIRONMENT_KEY,
    MAINNET_SUI_URL: "mainnet"
}

def sui_addresses(client: SyncClient) -> None:
    """Print all addresses."""
    all_add: list = client.config.addresses
    aliases = client.config.aliases
    cur_url = client.config.rpc_url

    # 獲取當前網絡環境名稱
    current_env = NETWORK_ENV_MAP.get(cur_url, "unknown").upper()

    print(f"Current network environment: {current_env}")
    print(f"Active address: {client.config.active_address}")
    print("All addresses:")
    for addr in all_add:
        print(f"  {addr}")
    print("Aliases:")
    for alias, addr in aliases.items():
        print(f"  {alias}: {addr}")

async def get_objects(client: AsyncClient, address: SuiAddress = None, object_type: str = None):
    """get tasksheet objects from active address with status == 1"""
    address = address or client.config.active_address
    
    builder = GetObjectsOwnedByAddress(address)
    result = await client.execute(builder)
    
    if result.is_ok():
        objects = result.result_data.data
        if object_type:
            objects = [obj for obj in objects if obj.object_type == object_type]
        
        print(f"Objects owned by {address} with status == 1:")
        for obj in objects:
            # 获取对象的详细信息
            print("all:",objects)
            object_read = await client.get_object(obj.object_id)
            
            if object_read.is_ok():
                content = object_read.result_data.content
                if content and hasattr(content, 'fields'):
                    status = content.fields.get('status')
                    if status == 1:
                        print(f"  ID: {obj.object_id}")
                        #print(f"  Type: {obj.object_type}")
                        if 'content' in content.fields:
                            print(f"  Content: {content.fields['content']}")
                        if 'main_task_id' in content.fields:
                            print(f"  Main Task ID: {content.fields['main_task_id']}")
                        #print(f"  Status: {status}")
                        print()
            else:
                print(f"  Error fetching object details: {object_read.result_string}")
    else:
        print(f"Error: {result.result_string}")


async def get_taskname_by_tasksheet(client: SyncClient, object_id: str, version: Optional[int] = None) -> None:
    """Show specific object."""
    sobject = await client.get_object(object_id, version)
    if sobject.is_ok():
        if isinstance(sobject.result_data, list):
            for item in sobject.result_data:
                data = json.loads(item.to_json())
                if 'content' in data and 'fields' in data['content'] and 'name' in data['content']['fields']:
                    print(data['content']['fields']['name'])
        else:
            data = json.loads(sobject.result_data.to_json())
            if 'content' in data and 'fields' in data['content'] and 'name' in data['content']['fields']:
                print(data['content']['fields']['name'])
    else:
        print(f"{sobject.result_string}")

async def main():
    cfg = SuiConfig.default_config()
    print(f"Using configuration from {os.environ.get(PYSUI_CLIENT_CONFIG_ENV, 'default location')}")

    client = AsyncClient(cfg)
    #sui_addresses(client)
    
    # 使用活躍地址獲取對象
    #get_objects(client)
    
    # 可選: 使用特定地址和對象類型
    # specific_address = SuiAddress("0x123456789abcdef...")  # 替換為實際地址
    #specific_address = client.config.active_address
    # specific_type = "0x2::coin::Coin<0x2::sui::SUI>"
    mod_cap_type = "0xc8e76738b2a255fe5a093a39f1eaa3b3ab869efcd62e4705c8790ceb7a532f02::public_task::ModCap"
    specific_type = "0xc8e76738b2a255fe5a093a39f1eaa3b3ab869efcd62e4705c8790ceb7a532f02::public_task::TaskSheet"
    await get_objects(client, object_type=specific_type)
    #await get_taskname_by_tasksheet(client, object_id="0xb770f9962ece25b4800ecdb0683d3d3713ad9ff33f6a8dec370dc6ee57078e18")
    #await get_objects(client, object_type=mod_cap_type)
    #await get_objects(client, specific_address)
    
if __name__ == "__main__":
    asyncio.run(main())