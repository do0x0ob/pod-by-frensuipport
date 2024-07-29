import warnings
from pysui import SyncClient, SuiConfig, handle_result
from pysui.sui.sui_txn import SyncTransaction
from pysui.sui.sui_types import ObjectID, SuiString
from constants import SUI_CLOCK_ID, TESTNET_PACKAGE_ID

warnings.filterwarnings("ignore", category=DeprecationWarning)

def approve_tasksheet(task_id: str, task_sheet_id: str, mod_cap_id: str, annotation: str):
    '''approve a tasksheet'''
    '''
    target: frensuipport testnet package function  --approve_and_send_reward
    arguments:
        task_id: main task id, get from currently displaying content associated main task object ID.
        task_sheet_id: tasksheet, get from currently displaying content object ID.
        mod_cap_id: mod cap id for the associated main task, get from config file.
        annotation: words by mod, get from TUI text input area.
    type_arguments: reward type associated with the main task, get from tasks_cache.json.
    '''
    client = SyncClient(SuiConfig.default_config())
    txn = SyncTransaction(client=client)


    # set move call target and params
    target = f"{TESTNET_PACKAGE_ID}::public_task::approve_and_send_reward"
    arguments = [
        ObjectID(task_id),
        ObjectID(task_sheet_id),
        SuiString(annotation),
        ObjectID(SUI_CLOCK_ID),
        ObjectID(mod_cap_id),
    ]
    type_arguments = ["0xe08560c1186b5d6cee1623c1a251f0879e998ded8c27f64302632f18cadea5f2::faucet_eyes::FAUCET_EYES"]  # type<T>

    # add move call order
    txn.move_call(
        target=target,
        arguments=arguments,
        type_arguments=type_arguments
    )

    # execute transaction and return result
    tx_result = handle_result(txn.execute())    
    return True if tx_result.effects.status.status == "success"  else False



# call function
#approve_tasksheet(task_id, task_sheet_id, mod_cap_id, annotation)