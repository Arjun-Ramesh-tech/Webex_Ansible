from ansible import context
from ansible.cli import CLI
from ansible.module_utils.common.collections import ImmutableDict
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
import filecmp
import shutil
import requests
import time
import configparser
import os


#Config File Read
config = configparser.ConfigParser()
config.read("Webex_Config.txt")

# Webex Variables
webex_token = config.get("configuration", "webex_token")
webex_roomName = config.get("configuration", "webex_roomName")
webex_roomId=None

def ansible():
    context.CLIARGS = ImmutableDict(tags={}, listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
                        module_path=None, forks=100, remote_user='xxx', private_key_file=None,
                        ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=False,
                        verbosity=True, check=False, start_at_task=None)
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=('inventory.txt',))
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    pbex = PlaybookExecutor(playbooks=['playbook.yaml'], inventory=inventory, variable_manager=variable_manager, loader=loader,passwords={})

    results = pbex.run()

def sendDataToWebex(dataToWebex):
    response = requests.post("https://webexapis.com/v1/messages",
                             headers={
                                 'Content-Type': 'application/json',
                                 'Authorization': 'Bearer ' + webex_token
                             },
                             json={
                                 'roomId': webex_roomId,
                                 'text': str(dataToWebex)
                             })

    print(response.status_code)
    if response.status_code == 200:
        print("Message Sent Successfully to Webex")
    else:
        raise Exception("Message Not Sent to Webex")

def fileGet():
    arr=os.listdir()
    print(arr)
    for i in arr:
        if i.endswith('_log.txt'):
            filecompare(i,i[0:-8])
            fileCopy(i,i[0:-8])

def filecompare(new_log,hostname):
    print("File Comparison In Progress")
    if not os.path.isfile(hostname+'_old.txt'):
        open(hostname+'_old.txt', "w+").close()
    if filecmp.cmp(new_log,hostname+'_old.txt'):
        print("Files are same")
    else:
        with open(new_log,'r') as f:
            lines=f.readlines()
        if lines[0].find('EOBC') ==-1:
            print("Not a Problem")
        else:
            device_detail='HOSTNAME:'+hostname+'\n'
            sendDataToWebex(device_detail+lines[0])

def fileCopy(new_log,hostname):
    print("Old Log has been stored for reference")
    shutil.copy(new_log,hostname+'_old.txt')

def getroomId():
    response=requests.get("https://webexapis.com/v1/rooms",
    headers={
            'Content-type':'application/json',
            'Authorization':'Bearer ' +webex_token
    }
    )
    flag=False
    roomsArr=response.json()['items']
    for i in roomsArr:
        if i['title']==webex_roomName:
            flag=True
            webex_roomId=i['id']
            break
    if flag==False:
        raise Exception("Room Name Not Present")
    else:
        return webex_roomId


if __name__ == "__main__":
    webex_roomId=getroomId()
    while True:
        ansible()
        print("Ansible has got the log files")
        fileGet()
        print("Iteration Over")
        time.sleep(20)



