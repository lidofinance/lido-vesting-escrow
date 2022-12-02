# @version 0.3.7

"""
@notice Dummy contract for selfDestruct transfer
"""


@external
@payable
def __default__():
    pass

@external
def destruct(recipient: address):
    selfdestruct(recipient)
