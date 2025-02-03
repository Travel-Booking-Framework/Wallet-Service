import grpc
from Wallet.models import Transaction, Wallet, TransactionStatus, TransactionType
import refund_gateway_pb2
import refund_gateway_pb2_grpc


class RefundProcessor:
    """
    RefundProcessor handles the refund (debit) operations using gRPC.
    It creates a Transaction record with a PENDING status and type 'debit',
    then sends its details to RefundService.
    """
    def __init__(self, grpc_target: str):
        # The target address for RefundService (e.g., 'localhost:50054')
        self.grpc_target = grpc_target

    def create_pending_refund_transaction(self, wallet: Wallet, amount: int, description: str = None) -> Transaction:
        """
        Create a new Transaction record with status PENDING for a refund.
        Note: Transaction type is set to 'debit' (reducing the wallet's balance).
        """
        try:
            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type=TransactionType.DEBIT.value,
                status=TransactionStatus.PENDING.value,
                description=description
            )
            return transaction
        except Exception as e:
            # Handle error during transaction creation (e.g., logging).
            print(f"Error creating refund transaction: {e}")
            return None

    def send_refund_transaction(self, transaction: Transaction):
        """
        Send the refund transaction details to RefundService via gRPC.
        """
        try:
            # Establish a channel to the RefundService.
            channel = grpc.insecure_channel(self.grpc_target)
            stub = refund_gateway_pb2_grpc.RefundGatewayStub(channel)
            # Build the RefundRequest message with transaction details.
            request = refund_gateway_pb2.RefundRequest(
                transaction_id=transaction.id,
                wallet_uuid=str(transaction.wallet.wallet_uuid),
                amount=transaction.amount,
                transaction_type=transaction.transaction_type,
                status=transaction.status,
                description=transaction.description if transaction.description else ""
            )
            # Call the ProcessRefund RPC.
            response = stub.ProcessRefund(request)
            print("Received response from RefundService:", response.status, response.message)
        except Exception as e:
            # Handle errors during the gRPC call.
            print(f"Error sending refund transaction via gRPC: {e}")

    def process_refund(self, wallet: Wallet, amount: int, description: str = None):
        """
        Process the refund by creating a pending refund transaction and sending
        its details to RefundService via gRPC.
        """
        transaction = self.create_pending_refund_transaction(wallet, amount, description)
        if transaction:
            self.send_refund_transaction(transaction)
        else:
            print("Failed to create refund transaction.")
