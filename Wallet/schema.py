import graphene
from graphene_django import DjangoObjectType
from Wallet.models import Wallet, Transaction


class WalletType(DjangoObjectType):
    class Meta:
        model = Wallet
        fields = ('wallet_uuid', 'national_code', 'balance')


class TransactionType(DjangoObjectType):
    # Add an extra field to include the wallet's national_code.
    national_code = graphene.String()

    class Meta:
        model = Transaction
        fields = ('id', 'wallet', 'amount', 'transaction_type', 'timestamp', 'status', 'description')

    def resolve_national_code(self, info):
        # Returns the national_code from the related Wallet instance.
        return self.wallet.national_code


class Query(graphene.ObjectType):
    # Query 1: Get all transactions for a user by national code.
    user_transactions = graphene.List(
        TransactionType,
        national_code=graphene.String(required=True),
        description="Returns all transactions for a user based on their national code."
    )

    # Query 2: Get wallet information for a user by national code.
    wallet_by_national_code = graphene.Field(
        WalletType,
        national_code=graphene.String(required=True),
        description="Returns the wallet information for a user based on their national code."
    )

    # Query 3: Get all transactions with the wallet's national code added.
    all_transactions_with_national_code = graphene.List(
        TransactionType,
        description="Returns all transactions along with the associated wallet's national code."
    )

    def resolve_user_transactions(root, info, national_code):
        try:
            wallet = Wallet.objects.get(national_code=national_code)
            return Transaction.objects.filter(wallet=wallet)
        except Wallet.DoesNotExist:
            return []

    def resolve_wallet_by_national_code(root, info, national_code):
        try:
            return Wallet.objects.get(national_code=national_code)
        except Wallet.DoesNotExist:
            return None

    def resolve_all_transactions_with_national_code(root, info):
        # Returns all Transaction objects. The 'national_code' field is added via the custom resolver in TransactionType.
        return Transaction.objects.all()


schema = graphene.Schema(query=Query)