import json

from brownie import network
from dotmap import DotMap

import utils.log as log


def load_json(file):
    try:
        return json.load(file)
    except json.JSONDecodeError:
        return {}


def read_or_update_state(stateUpdate={}):
    deployed_filename = f"./deployed-{network.show_active()}.json"
    with open(deployed_filename, "a+") as fp:
        fp.seek(0)
        state = load_json(fp)
        if stateUpdate:
            state = {**state, **stateUpdate}
            fp.seek(0)
            fp.truncate()
            json.dump(state, fp, indent=4)
            log.info("Saving metadata to", deployed_filename)
        fp.close()
    return DotMap(state)
