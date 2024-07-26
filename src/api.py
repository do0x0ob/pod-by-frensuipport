#from typing import Optional
from pysui import SuiConfig, AsyncClient
from pysui.sui.sui_types.address import SuiAddress
from pysui.sui.sui_builders.get_builders import GetObjectsOwnedByAddress
from pysui.sui.sui_constants import PYSUI_CLIENT_CONFIG_ENV
import os
import asyncio
import warnings
#import json
from constants import NETWORK_ENV_MAP, OBJECT_TYPE_ADDRESSES
warnings.filterwarnings("ignore", category=DeprecationWarning)

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
            object_read = await client.get_object(obj.object_id)
            
            if object_read.is_ok():
                content = object_read.result_data.content
                if content and hasattr(content, 'fields'):
                    status = content.fields.get('status')
                    if status == 1:
                        print(f"  ID: {obj.object_id}")
                        if 'content' in content.fields:
                            print(f"  Content: {content.fields['content']}")
                        if 'main_task_id' in content.fields:
                            print(f"  Main Task ID: {content.fields['main_task_id']}")
                        print()
            else:
                print(f"  Error fetching object details: {object_read.result_string}")
    else:
        print(f"Error: {result.result_string}")


async def main():
    cfg = SuiConfig.default_config()
    print(f"Using configuration from {os.environ.get(PYSUI_CLIENT_CONFIG_ENV, 'default location')}")

    client = AsyncClient(cfg)
    current_env = NETWORK_ENV_MAP.get(client.config.rpc_url, "unknown")
    tasksheet_address = OBJECT_TYPE_ADDRESSES["TASKSHEET"].get(current_env)
    await get_objects(client, object_type=tasksheet_address)


if __name__ == "__main__":
    asyncio.run(main())
