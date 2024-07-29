import os
import json
import warnings
from typing import Optional, Tuple
from pysui import SuiConfig, AsyncClient
from pysui.sui.sui_types.address import SuiAddress
from pysui.sui.sui_builders.get_builders import GetObjectsOwnedByAddress
from pysui.sui.sui_constants import PYSUI_CLIENT_CONFIG_ENV
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
    """Get all tasksheet objects from active address with status == 1"""
    address = address or client.config.active_address

    tasksheets = {}
    status_1_count = 0
    total_objects = 0
    cursor = None

    while True:
        builder = GetObjectsOwnedByAddress(address, cursor=cursor, limit=50)
        result = await client.execute(builder)

        if not result.is_ok():
            print(f"Error: {result.result_string}")
            break

        page_data = result.result_data
        objects = page_data.data
        total_objects += len(objects)

        if object_type:
            objects = [obj for obj in objects if obj.object_type == object_type]

        for obj in objects:
            object_read = await client.get_object(obj.object_id)

            if object_read.is_ok():
                content = object_read.result_data.content
                if hasattr(content, 'fields'):
                    status = content.fields.get('status')
                    if status == 1:
                        status_1_count += 1
                        if not object_type or obj.object_type == object_type:
                            tasksheets[obj.object_id] = {
                                "maintask_id": content.fields.get('main_task_id', ''),
                                "content": content.fields.get('content', '')
                            }
            else:
                print(f"Error fetching object details: {object_read.result_string}")

        cursor = page_data.next_cursor if page_data.has_next_page else None
        if cursor is None:
            break  # No more objects, exit the loop

    return tasksheets


async def get_taskname_and_rewardtype_by_tasksheet(client: AsyncClient, object_id: str, version: Optional[int] = None) -> Tuple[str, str, str]:
    """get task name, reward type, and main task id by tasksheet"""
    sobject = await client.get_object(object_id, version)

    if sobject.is_ok():
        data = json.loads(sobject.result_data.to_json())
        if 'content' in data and 'fields' in data['content']:
            task_name = data['content']['fields'].get('name', 'Unknown Task')
            object_type = data['content']['type']
            reward_type = object_type.split('<')[1].split('>')[0] if '<' in object_type and '>' in object_type else ''
            main_task_id = data['content']['fields'].get('main_task_id', '')
            print(task_name, reward_type, main_task_id)
            return task_name, reward_type, main_task_id
    return "Unknown Task", "", ""


async def assemble_submissions_list(client: AsyncClient, tasksheets: dict) -> dict:
    global TASKS
    SUBMISSIONS = {}
    tasks_updated = False

    for tasksheet_id, tasksheet_data in tasksheets.items():
        maintask_id = tasksheet_data['maintask_id']
        content = tasksheet_data['content']

        task_name, reward_type = TASKS.get(maintask_id, (None, None))
        if task_name is None:
            task_name, reward_type = await get_taskname_and_rewardtype_by_tasksheet(client, maintask_id)
            TASKS[maintask_id] = (task_name, reward_type)
            tasks_updated = True

        if task_name not in SUBMISSIONS:
            SUBMISSIONS[task_name] = {
                "reward_type": reward_type,
                "maintask_id": maintask_id,
                "tasksheets": {}
            }

        SUBMISSIONS[task_name]["tasksheets"][tasksheet_id] = {
            "content": content,
            "maintask_id": maintask_id
        }

    if tasks_updated:
        save_tasks(TASKS)

    return SUBMISSIONS


async def get_submissions():
    cfg = SuiConfig.default_config()
    print(f"Using configuration from {os.environ.get(PYSUI_CLIENT_CONFIG_ENV, 'default location')}")

    client = AsyncClient(cfg)
    current_env = NETWORK_ENV_MAP.get(client.config.rpc_url, "unknown")
    tasksheet_address = OBJECT_TYPE_ADDRESSES["TASKSHEET"].get(current_env)

    if not tasksheet_address:
        print(f"No TASKSHEET address found for environment: {current_env}")
        return {}

    tasksheets = await get_tasksheets(client, object_type=tasksheet_address)
    submissions = await assemble_submissions_list(client, tasksheets)

    markdown_contents = {
        tasksheet_id: submission_data['content'] + "\n\n"
        for task_submissions in submissions.values()
        for tasksheet_id, submission_data in task_submissions["tasksheets"].items()
    }


    task_info = {}
    for task_name, task_data in submissions.items():
        task_info[task_name] = {
            "reward_type": task_data["reward_type"],
            "maintask_id": task_data["maintask_id"],
            "tasksheets": {}
        }
        for tasksheet_id, submission_data in task_data["tasksheets"].items():
            task_info[task_name]["tasksheets"][tasksheet_id] = {
                "content": submission_data["content"],
                "maintask_id": submission_data["maintask_id"]
            }



    markdown_file_path = 'markdown_contents.json'
    with open(markdown_file_path, 'w', encoding='utf-8') as f:
        json.dump(markdown_contents, f, ensure_ascii=False, indent=2)
    
    print(f"Markdown contents have been written to {markdown_file_path}")


    task_info_file_path = 'task_info.json'
    with open(task_info_file_path, 'w', encoding='utf-8') as f:
        json.dump(task_info, f, ensure_ascii=False, indent=2)
    
    print(f"Task info has been written to {task_info_file_path}")
    #print("debug", submissions)
    return submissions

"""
if __name__ == "__main__":
    asyncio.run(get_submissions())
"""