#these models are imported becuase SQLAlchemy needs to know about my models before their tables can be created.

from app.models.user import User
from app.models.wallet import Wallet
#these two above impoets make user and wallet registered when the module is imported


from app.models.ledger.transaction import LedgerTransaction
from app.models.ledger.entry import LedgerEntry

"""
The two above imports are important because Base.metadata.create_all() must  know about the models before it  creates the
tables.

"""
