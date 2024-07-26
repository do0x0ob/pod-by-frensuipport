from typing import Optional
from pysui import SuiConfig, AsyncClient
from pysui.sui.sui_types.address import SuiAddress
from pysui.sui.sui_builders.get_builders import GetObjectsOwnedByAddress
from pysui.sui.sui_constants import PYSUI_CLIENT_CONFIG_ENV
import os
import asyncio
import warnings
import json
from constants import NETWORK_ENV_MAP, OBJECT_TYPE_ADDRESSES, TASKS_FILE
warnings.filterwarnings("ignore", category=DeprecationWarning)

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

TASKS = load_tasks()

async def get_tasksheets(client: AsyncClient, address: SuiAddress = None, object_type: str = None):
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


async def get_taskname_by_tasksheet(client: AsyncClient, object_id: str, version: Optional[int] = None) -> str:
    """get task name by tasksheet"""
    sobject = await client.get_object(object_id, version)
    if sobject.is_ok():
        if isinstance(sobject.result_data, list):
            for item in sobject.result_data:
                data = json.loads(item.to_json())
                if 'content' in data and 'fields' in data['content'] and 'name' in data['content']['fields']:
                    return data['content']['fields']['name']
        else:
            data = json.loads(sobject.result_data.to_json())
            if 'content' in data and 'fields' in data['content'] and 'name' in data['content']['fields']:
                return data['content']['fields']['name']
    return "Unknown Task"


async def assemble_submissions_list(client: AsyncClient, tasksheets: dict) -> dict:
    """
    Organize the tasksheets into the required SUBMISSIONS structure
    """
    global TASKS
    SUBMISSIONS = {}
    tasks_updated = False

    for tasksheet_id, tasksheet_data in tasksheets.items():
        maintask_id = tasksheet_data['maintask_id']
        content = tasksheet_data['content']

        # Check if maintask_id is in TASKS
        if maintask_id not in TASKS:
            # If not, fetch the maintask name from the network
            task_name = await get_taskname_by_tasksheet(client, maintask_id)
            TASKS[maintask_id] = task_name
            tasks_updated = True
        else:
            task_name = TASKS[maintask_id]

        # Add data to the SUBMISSIONS dictionary
        if task_name not in SUBMISSIONS:
            SUBMISSIONS[task_name] = {}
        
        SUBMISSIONS[task_name][tasksheet_id] = {"content": content}

    # If TASKS has been updated, save to file
    if tasks_updated:
        save_tasks(TASKS)

    return SUBMISSIONS

async def main():
    cfg = SuiConfig.default_config()
    print(f"Using configuration from {os.environ.get(PYSUI_CLIENT_CONFIG_ENV, 'default location')}")

    client = AsyncClient(cfg)
    current_env = NETWORK_ENV_MAP.get(client.config.rpc_url, "unknown")
    tasksheet_address = OBJECT_TYPE_ADDRESSES["TASKSHEET"].get(current_env)
    
    if tasksheet_address:
        tasksheets = await get_tasksheets(client, object_type=tasksheet_address)
        submissions = await assemble_submissions_list(client, tasksheets)
        print("Submissions:")
        print(json.dumps(submissions, indent=2))
        
        print("\nUpdated TASKS:")
        print(json.dumps(TASKS, indent=2))
    else:
        print(f"No TASKSHEET address found for environment: {current_env}")


if __name__ == "__main__":
    asyncio.run(main())
