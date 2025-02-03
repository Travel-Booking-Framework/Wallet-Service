import grpc
from concurrent import futures
import time

from Wallet.models import Transaction, Wallet, TransactionStatus, TransactionType
import refund_callback_pb2
import refund_callback_pb2_grpc

class RefundCallbackServicer(refund_callback_pb2_grpc.RefundCallbackServicer):
    """
    RefundCallbackServicer receives callbacks from RefundService.
    If the refund transaction's status is 'completed' and type is 'debit',
    it subtracts the transaction amount from the Wallet's balance and updates the Transaction.
    """
    def ProcessRefundCallback(self, request, context):
        try:
            # Extract refund transaction details from the callback.
            transaction_id = request.transaction_id
            status = request.status
            transaction_type = request.transaction_type
            amount = request.amount
            wallet_uuid = request.wallet_uuid

            # Check if the refund is completed and is of type debit.
            if status.lower() == "completed" and transaction_type.lower() == "debit":
                # Retrieve the wallet using wallet_uuid.
                wallet = Wallet.objects.get(wallet_uuid=wallet_uuid)
                # Decrease the wallet balance by the refund amount.
                wallet.balance -= amount
                wallet.save()

                # Optionally update the Transaction record status to COMPLETED.
                try:
                    transaction = Transaction.objects.get(id=transaction_id)
                    transaction.status = TransactionStatus.COMPLETED.value
                    transaction.save()
                except Transaction.DoesNotExist:
                    # Transaction record not found; handle if needed.
                    pass

            # Return a success response.
            return refund_callback_pb2.RefundResponse(
                status="SUCCESS",
                message="Refund callback processed successfully."
            )
        except Exception as e:
            # Handle any errors during callback processing.
            context.set_details(f"Error processing refund callback: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return refund_callback_pb2.RefundResponse(
                status="FAILED",
                message="Failed to process refund callback."
            )

def serve():
    """
    Start the gRPC server to listen for refund callbacks.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    refund_callback_pb2_grpc.add_RefundCallbackServicer_to_server(RefundCallbackServicer(), server)
    server.add_insecure_port('[::]:50055')  # Port for refund callbacks.
    server.start()
    print("RefundCallback gRPC server started on port 50055.")
    try:
        while True:
            time.sleep(86400)  # Keep the server running.
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
