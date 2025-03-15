

from dataclasses import dataclass


@dataclass
class MaybeTransactions:
    Date: str
    Amount: str
    Account: str
    Category: str
    Tags: str
    Notes: str