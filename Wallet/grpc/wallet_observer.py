# This file contains the Observer implementation for the Create Wallet operation.

from Wallet.grpc.observer import Observer
from Wallet.models import Wallet


class WalletCreationObserver(Observer):
    def update(self, national_code: str):
        """
        Upon receiving a national_code, perform the Create Wallet operation.
        """
        # Create a wallet if it does not exist. If it exists, handle accordingly.
        try:
            wallet, created = Wallet.objects.get_or_create(national_code=national_code)
            if created:
                # Wallet was successfully created.
                # You can add logging or any additional operations here.
                pass
            else:
                # Wallet already exists.
                pass
        except Exception as e:
            # Error handling can be implemented here as needed.
            pass
