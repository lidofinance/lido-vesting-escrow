"""
Invocation:
    python -m scripts.safe_delegates cmd args
  or
    brownie run safe_delegates cmd args
"""
import os
import sys
import time

import requests
from eth_utils.address import to_checksum_address
from eth_utils.conversions import to_hex
from requests.models import HTTPError
from utils import log
from utils.helpers import proceedPrompt
from web3 import Web3

TX_SERVICE_BASE_URL = "https://safe-transaction.mainnet.gnosis.io"
SAFE_ADDRESS = os.getenv("SAFE_ADDRESS")
if not SAFE_ADDRESS:
    raise RuntimeError("SAFE_ADDRESS environment variable is not set")


def list():
    """List the Safe delegates"""
    response = requests.get(f"{TX_SERVICE_BASE_URL}/api/v1/safes/{SAFE_ADDRESS}/delegates")
    _raise_for_status(response)
    log.info("Delegates list:")
    for obj in response.json()["results"]:
        log.info(obj["delegate"])
    if not response.json()["results"]:
        log.info("[]")


def add(delegate: str, label: str):
    """Add delegate to Safe"""
    try:
        delegate = to_checksum_address(delegate)
    except ValueError as e:
        raise ValueError("Wrong delegate's address given") from e

    msg = _get_totp_msg(delegate)
    signature = sign_msg(msg)
    proceedPrompt()

    payload = {
        "safe": SAFE_ADDRESS,
        "delegate": delegate,
        "signature": signature,
        "label": label,
    }

    response = requests.post(
        f"{TX_SERVICE_BASE_URL}/api/v1/safes/{SAFE_ADDRESS}/delegates/",
        json=payload,
        headers={"Content-type": "application/json"},
    )

    _raise_for_status(response)
    log.okay("Delegates updated")
    list()


def remove(delegate: str):
    """Remove the given delegate from the Safe"""
    try:
        delegate = to_checksum_address(delegate)
    except ValueError as e:
        raise ValueError("Wrong delegate's address given") from e

    msg = _get_totp_msg(delegate)
    signature = sign_msg(msg)
    proceedPrompt()

    payload = {"signature": signature}
    response = requests.delete(
        f"{TX_SERVICE_BASE_URL}/api/v1/safes/{SAFE_ADDRESS}/delegates/{delegate}/",
        json=payload,
        headers={"Content-type": "application/json"},
    )

    _raise_for_status(response)
    log.okay("Delegate removed")
    list()


def sign_msg(msg: str) -> str:
    if log.prompt_yes_no("sign with frame?"):
        return _sign_with_frame(msg)
    print(f"Please, sign the following message: '{msg}' (without quotes) and past the signature back")
    return input("Signature: ").strip()


def _sign_with_frame(msg: str) -> str:
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:1248", {"timeout": 300}))  # frame
    if not w3.isConnected():
        raise RuntimeError("Expected frame to be running")

    signer = input("Signer's address: ")
    s = w3.eth.sign(signer, text=msg)
    return to_hex(s)


def _get_totp_msg(delegate: str) -> str:
    totp = int(time.time()) // 3600
    totp_life = (totp + 1) * 3600 - int(time.time())
    log.warn(f"TOTP expires in {totp_life} seconds")
    return delegate + str(totp)


def _raise_for_status(r: requests.Response) -> None:
    """Thin wrapper for the better readability"""
    try:
        r.raise_for_status()
    except HTTPError as e:
        raise HTTPError(r.text) from e


def _abort_execution():
    log.error("Program halted!")
    exit(1)


if __name__ == "__main__":  # module-like invocation
    try:
        _, cmd, *args = sys.argv
    except ValueError:
        log.error("Usage: python -m scripts.safe_delegates cmd ...args")
        _abort_execution()

    if cmd not in vars():
        log.error("cmd: one of list|add|remove")
        _abort_execution()

    from inspect import signature

    fun = locals()[cmd]
    sig = signature(fun)
    if len(args) != len(sig.parameters):
        log.error("cmd: unexpected sequence of arguments")
        _abort_execution()

    fun(*args)
