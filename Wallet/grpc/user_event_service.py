# # This file contains the implementation of the gRPC Server that receives user event data (with national_code).
# # It uses the Observer pattern to trigger the Create Wallet operation and includes error handling.
#
# import grpc
# from concurrent import futures
# import time
#
# # Import the generated classes from the protobuf file.
# #import user_event_pb2
# #import user_event_pb2_grpc
#
# from Wallet.grpc.observer import Subject
# from Wallet.grpc.wallet_observer import WalletCreationObserver
#
#
# class UserEventServicer(user_event_pb2_grpc.UserEventServiceServicer):
#     def __init__(self):
#         # Create a Subject to manage observers.
#         self.subject = Subject()
#         # Attach the WalletCreationObserver to the Subject.
#         self.subject.attach(WalletCreationObserver())
#
#     def CreateUserEvent(self, request, context):
#         """
#         This method is called via gRPC when a user creation event (with national_code) is received.
#         """
#         try:
#             national_code = request.national_code  # Retrieve the national code from the gRPC request.
#             # Notify all attached observers (e.g., WalletCreationObserver) using the Observer pattern.
#             self.subject.notify(national_code)
#             # Return a successful response.
#             #return user_event_pb2.CreateUserEventResponse(status="SUCCESS")
#         except Exception as e:
#             # Error handling: set gRPC error details and status code.
#             context.set_details('Error occurred: ' + str(e))
#             context.set_code(grpc.StatusCode.INTERNAL)
#             #return user_event_pb2.CreateUserEventResponse(status="FAILED")
#
# def serve():
#     """
#     Start the gRPC Server.
#     """
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     #user_event_pb2_grpc.add_UserEventServiceServicer_to_server(UserEventServicer(), server)
#     server.add_insecure_port('[::]:50051')
#     server.start()
#     try:
#         while True:
#             time.sleep(86400)  # Keep the server running.
#     except KeyboardInterrupt:
#         server.stop(0)
#
#
# if __name__ == '__main__':
#     serve()
