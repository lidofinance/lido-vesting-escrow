def mint_or_transfer_for_testing(owner, recipient, token, balance, deployed):
    if deployed:
        if recipient != owner:
            token.transfer(recipient, balance, {"from": owner})
    else:
        token._mint_for_testing(balance, {"from": recipient})
