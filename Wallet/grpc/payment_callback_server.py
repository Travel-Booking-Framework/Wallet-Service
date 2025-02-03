import grpc
from concurrent import futures
import time

from Wallet.models import Transaction, Wallet, TransactionStatus, TransactionType
import payment_callback_pb2
import payment_callback_pb2_grpc


class PaymentCallbackServicer(payment_callback_pb2_grpc.PaymentCallbackServicer):
    """
    PaymentCallbackServicer receives callbacks from PaymentGatewayService.
    If the transaction status is 'completed' and the transaction type is 'credit',
    it adds the transaction amount to the Wallet's balance.
    """
    def ProcessPaymentCallback(self, request, context):
        try:
            # Extract transaction details from the callback request.
            transaction_id = request.transaction_id
            status = request.status
            transaction_type = request.transaction_type
            amount = request.amount
            wallet_uuid = request.wallet_uuid

            # Check if the transaction is completed and is of type credit.
            if status.lower() == "completed" and transaction_type.lower() == "credit":
                # Retrieve the wallet using wallet_uuid.
                wallet = Wallet.objects.get(wallet_uuid=wallet_uuid)
                # Increase wallet balance by the transaction amount.
                wallet.balance += amount
                wallet.save()

                # Optionally update the Transaction record status to COMPLETED.
                try:
                    transaction = Transaction.objects.get(id=transaction_id)
                    transaction.status = TransactionStatus.COMPLETED.value
                    transaction.save()
                except Transaction.DoesNotExist:
                    # Transaction record was not found; handle accordingly.
                    pass

            # Return a success response.
            return payment_callback_pb2.TransactionResponse(
                status="SUCCESS",
                message="Callback processed successfully."
            )
        except Exception as e:
            # Handle any errors during callback processing.
            context.set_details(f"Error processing payment callback: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return payment_callback_pb2.TransactionResponse(
                status="FAILED",
                message="Failed to process callback."
            )

def serve():
    """
    Starts the gRPC server to listen for payment callbacks.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    payment_callback_pb2_grpc.add_PaymentCallbackServicer_to_server(PaymentCallbackServicer(), server)
    server.add_insecure_port('[::]:50053')  # Listening port for callbacks.
    server.start()
    print("PaymentCallback gRPC server started on port 50053.")
    try:
        while True:
            time.sleep(86400)  # Keep the server running.
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
