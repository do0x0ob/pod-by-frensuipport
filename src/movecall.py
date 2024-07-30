import warnings
from pysui import SyncClient, SuiConfig, handle_result
from pysui.sui.sui_txn import SyncTransaction
from pysui.sui.sui_types import ObjectID, SuiString
from constants import SUI_CLOCK_ID, TESTNET_PACKAGE_ID

warnings.filterwarnings("ignore", category=DeprecationWarning)

def approve_tasksheet(reward_type: str, task_id: str, task_sheet_id: str, mod_cap_id: str, annotation: str):
    """approve a tasksheet"""
    """
    target: frensuipport testnet package function  --approve_and_send_reward
    arguments:
        task_id: main task id, get from currently displaying content associated main task object ID.
        task_sheet_id: tasksheet, get from currently displaying content object ID.
        mod_cap_id: mod cap id for the associated main task, get from config file.
        annotation: words by mod, get from TUI text input area.
    type_arguments: reward type associated with the main task, get from tasks_cache.json.
    """
    client = SyncClient(SuiConfig.default_config())
    txn = SyncTransaction(client=client)

    # set move call target and params
    target = f"{TESTNET_PACKAGE_ID}::public_task::approve_and_send_reward"
    arguments = [
        ObjectID(task_id),
        ObjectID(task_sheet_id),
        SuiString(annotation),
        ObjectID(SUI_CLOCK_ID),
        ObjectID(mod_cap_id)
    ]
    
    type_arguments = [reward_type]

    # add move call order
    txn.move_call(
        target=target,
        arguments=arguments,
        type_arguments=type_arguments
    )

    # execute transaction and return result
    tx_result = handle_result(txn.execute())    
    return True if tx_result.effects.status.status == "success"  else False


def reject_tasksheet(task_sheet_id: str, mod_cap_id: str, annotation: str):
    """reject and return tasksheet to submitter"""
    """
    target: frensuipport testnet package function  --reject_and_return_task_sheet
    arguments:
        task_sheet_id: tasksheet, get from currently displaying content object ID.
        annotation: words by mod, get from TUI text input area.
    """
    client = SyncClient(SuiConfig.default_config())
    txn = SyncTransaction(client=client)

    target = f"{TESTNET_PACKAGE_ID}::public_task::reject_and_return_task_sheet"
    arguments = [
        ObjectID(task_sheet_id),
        SuiString(annotation),
        ObjectID(SUI_CLOCK_ID),
        ObjectID(mod_cap_id)
    ]

    txn.move_call(
        target=target,
        arguments=arguments,
    )

    tx_result = handle_result(txn.execute())
    return True if tx_result.effects.status.status == "success" else False

# for test only
task_sheet_id = "0x77aafda59464930e32f3198fe42d710020ed96be1d016038ba5997c90910cc04"
mod_cap_id = "0x263c23fd72b08bda2adec5298c797f35e9f2e9d87043b6efeb773a5b202faa5c"
annotation = "test"

if __name__ == "__main__":
    reject_tasksheet(task_sheet_id, mod_cap_id, annotation)
    