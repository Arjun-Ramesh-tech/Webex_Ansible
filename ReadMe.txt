1)Create a ansibel_host_key environment variable to stop host key checking
    export ANSIBLE_HOST_KEY_CHECKING=False

2)Change the webex_config.txt file
    Give the webex api key and webex room name

3)Change the inventory.txt file to match your device details

4)The Playbook will execute the command sh logging | i EOBC heartbeat failure and get the output to python

5)Python will use ansible to get the details and verify the output.if changes are present it will notify via webex


