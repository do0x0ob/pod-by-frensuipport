#from typing import Optional
from pysui import SuiConfig, AsyncClient
from pysui.sui.sui_types.address import SuiAddress
from pysui.sui.sui_builders.get_builders import GetObjectsOwnedByAddress
from pysui.sui.sui_constants import PYSUI_CLIENT_CONFIG_ENV
import os
import asyncio
import warnings
import json
from constants import NETWORK_ENV_MAP, OBJECT_TYPE_ADDRESSES
warnings.filterwarnings("ignore", category=DeprecationWarning)

async def get_objects(client: AsyncClient, address: SuiAddress = None, object_type: str = None):
    """Get tasksheet objects from active address with status == 1"""
    address = address or client.config.active_address
    
    builder = GetObjectsOwnedByAddress(address)
    result = await client.execute(builder)
    
    tasksheets = {}
    
    if result.is_ok():
        objects = result.result_data.data
        if object_type:
            objects = [obj for obj in objects if obj.object_type == object_type]
        
        for obj in objects:
            object_read = await client.get_object(obj.object_id)
            
            if object_read.is_ok():
                content = object_read.result_data.content
                if content and hasattr(content, 'fields'):
                    status = content.fields.get('status')
                    if status == 1:
                        tasksheet_id = obj.object_id
                        main_task_id = content.fields.get('main_task_id', '')
                        content_text = content.fields.get('content', '')
                        
                        tasksheets[tasksheet_id] = {
                            "maintask_id": main_task_id,
                            "content": content_text,
                        }
            else:
                print(f"Error fetching object details: {object_read.result_string}")
    else:
        print(f"Error: {result.result_string}")
    
    return tasksheets

async def main():
    cfg = SuiConfig.default_config()
    print(f"Using configuration from {os.environ.get(PYSUI_CLIENT_CONFIG_ENV, 'default location')}")

    client = AsyncClient(cfg)
    current_env = NETWORK_ENV_MAP.get(client.config.rpc_url, "unknown")
    tasksheet_address = OBJECT_TYPE_ADDRESSES["TASKSHEET"].get(current_env)

    if tasksheet_address:
        tasksheets = await get_objects(client, object_type=tasksheet_address)
        print("Tasksheets:")
        print(json.dumps(tasksheets, indent=2))
    else:
        print(f"No TASKSHEET address found for environment: {current_env}")


if __name__ == "__main__":
    asyncio.run(main())
