import time
from typing import Any
from pymemuc import PyMemuc

pmc = PyMemuc()

# stop all running vms
pmc.stop_all_vm()

# get list of vms on machine
vms:list[dict[str,Any]] = pmc.list_vm_info() # type: ignore

# find vm named pyclashbot
found = any(vm['title'] == "pyclashbot" for vm in vms)

if not found:
    # create a vm named pyclashbot
    vm_index = pmc.create_vm()
    # rename the vm to pyclashbot
    pmc.rename_vm(vm_index, new_name="pyclashbot")
else:
    # find the index of the vm named pyclashbot
    vm_index = next(vm['index'] for vm in vms if vm['title'] == "pyclashbot")

# configure the vm
pmc.set_configuration_vm("is_customed_resolution", "1", vm_index=vm_index)
pmc.set_configuration_vm("resolution_width", "460", vm_index=vm_index)
pmc.set_configuration_vm("resolution_height", "680", vm_index=vm_index)
pmc.set_configuration_vm("vbox_dpi", "160", vm_index=vm_index)
pmc.set_configuration_vm("start_window_mode", "1", vm_index=vm_index) # set to remember window location

# start the vm
pmc.start_vm(vm_index=vm_index)

# wait 5 seconds for ad to load
time.sleep(10)

# send home button click
pmc.trigger_keystroke_vm("home", vm_index=vm_index)

# wait for some time
time.sleep(30)

# close the vm
pmc.stop_vm(vm_index=vm_index)


