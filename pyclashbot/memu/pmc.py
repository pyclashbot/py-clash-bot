"""This module provides a PyMemuc singleton instance."""

import logging
import sys
from os.path import join

from pymemuc import PyMemuc, PyMemucError, VMInfo

FROZEN = getattr(sys, "frozen", False)

pmc = PyMemuc()

adb_path = join(
    # pylint: disable=protected-access
    pmc._get_memu_top_level(),
    "adb.exe",
)


def get_vm_index(name: str) -> int:
    """Get the index of the vm with the given name"""
    # get list of vms on machine
    vms: list[VMInfo] = pmc.list_vm_info()

    # sorted by index, lowest to highest
    vms.sort(key=lambda x: x["index"])

    # get the indecies of all vms named pyclashbot
    vm_indices: list[int] = [vm["index"] for vm in vms if vm["title"] == name]

    # delete all vms except the lowest index, keep looping until there is only one
    while len(vm_indices) > 1:
        # as long as no exception is raised, this while loop should exit on first iteration
        for vm_index in vm_indices[1:]:
            try:
                pmc.delete_vm(vm_index)
                vm_indices.remove(vm_index)
            except PyMemucError as err:
                logging.exception(err)

    # return the index. if no vms named pyclashbot exist, return -1
    return vm_indices[0] if vm_indices else -1
