import grpc
from Wallet.models import Transaction, Wallet, TransactionStatus, TransactionType
import payment_gateway_pb2
import payment_gateway_pb2_grpc


class PaymentProcessor:
    """
    PaymentProcessor is responsible for:
      1. Creating a Transaction record with status PENDING.
      2. Sending the Transaction data to PaymentGatewayService via gRPC.
    """
    def __init__(self, grpc_target: str):
        # The target address for PaymentGatewayService (e.g., 'localhost:50052')
        self.grpc_target = grpc_target

    def create_pending_transaction(self, wallet: Wallet, amount: int, description: str = None) -> Transaction:
        """
        Create a new Transaction record with a PENDING status.
        Note: Transaction type is set to 'credit' (only increases are processed).
        """
        try:
            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type=TransactionType.CREDIT.value,
                status=TransactionStatus.PENDING.value,
                description=description
            )
            return transaction
        except Exception as e:
            # Handle error during transaction creation (e.g., logging).
            print(f"Error creating transaction: {e}")
            return None

    def send_transaction(self, transaction: Transaction):
        """
        Send the Transaction data to the PaymentGatewayService via gRPC.
        """
        try:
            channel = grpc.insecure_channel(self.grpc_target)
            stub = payment_gateway_pb2_grpc.PaymentGatewayStub(channel)
            request = payment_gateway_pb2.TransactionRequest(
                transaction_id=transaction.id,
                wallet_uuid=str(transaction.wallet.wallet_uuid),
                amount=transaction.amount,
                transaction_type=transaction.transaction_type,
                status=transaction.status,
                description=transaction.description if transaction.description else ""
            )
            response = stub.ProcessTransaction(request)
            print("Received response from PaymentGatewayService:", response.status, response.message)
        except Exception as e:
            # Handle errors during the gRPC call.
            print(f"Error sending transaction via gRPC: {e}")

    def process_payment(self, wallet: Wallet, amount: int, description: str = None):
        """
        Process the payment by creating a pending transaction and sending its data to PaymentGatewayService.
        """
        transaction = self.create_pending_transaction(wallet, amount, description)
        if transaction:
            self.send_transaction(transaction)
        else:
            print("Failed to create pending transaction.")
