# WalletService Microservice

## Overview

**WalletService** is a Django-based microservice responsible for managing wallet operations such as creating wallets and processing transactions. It interacts with two external microservices via gRPC:
  
- **PaymentGatewayService:** Handles credit (balance increase) transactions.
- **RefundService:** Handles debit (refund) transactions.

The service also listens for user events (from another microservice) to create new wallet records.

## Architecture and Design

WalletService follows a modular microservices architecture and leverages the following design patterns:

### Design Patterns Used

- **Observer Pattern:**  
  Used to decouple event detection from processing. For example, when a user event (with a national code) is received, the `WalletCreationObserver` is notified to create or update a wallet. Similarly, callback observers are used to update wallet balances when external services (PaymentGateway or Refund) send back transaction updates.

- **gRPC Client/Server Pattern:**  
  Utilizes gRPC for efficient, contract-based communication with external services. Outbound gRPC clients send transaction data to PaymentGatewayService and RefundService, while inbound gRPC servers handle callbacks to update wallet balances based on transaction outcomes.

## Microservice Operations

### 1. Payment Operations (Credit)

- **Operation:**  
  - When a credit (top-up) operation is initiated, a new `Transaction` record is created in the database with a **PENDING** status and type set to **credit**.
  
- **Outbound gRPC Call:**  
  - The `PaymentProcessor` sends the transaction details to the external **PaymentGatewayService** via gRPC.

- **Inbound Callback:**  
  - PaymentGatewayService later calls back using the `PaymentCallback` service.
  - On receiving a callback with status **completed** and transaction type **credit**, WalletService updates the corresponding wallet’s balance by **adding** the transaction amount.
  - The Transaction record is updated to reflect the **COMPLETED** status.

### 2. Refund Operations (Debit)

- **Operation:**  
  - For refund (debit) operations, a new `Transaction` record is created with a **PENDING** status and type set to **debit**.
  
- **Outbound gRPC Call:**  
  - The `RefundProcessor` sends the refund transaction details to the external **RefundService** via gRPC.

- **Inbound Callback:**  
  - RefundService later sends a callback using the `RefundCallback` service.
  - If the callback indicates that the transaction is **completed** and the type is **debit**, WalletService subtracts the refund amount from the corresponding wallet’s balance.
  - The Transaction record is updated to **COMPLETED**.

### 3. User Event Processing

- **Operation:**  
  - When a user is created in another microservice, a user event (including the user's national code) is sent to WalletService.
  
- **Processing:**  
  - The event is received (e.g., via a dedicated gRPC endpoint) and the Observer pattern (through `WalletCreationObserver`) is used to create a new wallet if one does not exist.

## Protobuf Files and gRPC Stub Generation

The following `.proto` files define the gRPC services:

- **`protos/payment_gateway.proto`:**  
  Defines the `PaymentGateway` service for processing credit transactions.

- **`protos/payment_callback.proto`:**  
  Defines the callback service to receive responses from PaymentGatewayService.

- **`protos/refund_gateway.proto`:**  
  Defines the `RefundGateway` service for processing debit (refund) transactions.

- **`protos/refund_callback.proto`:**  
  Defines the callback service to receive responses from RefundService.

- **`protos/user_event.proto`:**  
  (If applicable) Defines the service for handling user events.

### Generating Python Stubs

From the project root (where the `protos/` directory is located), run the following commands:

```bash
python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/payment_gateway.proto
python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/payment_callback.proto
python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/refund_gateway.proto
python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/refund_callback.proto
python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/user_event.proto
```

This will generate the necessary Python files (e.g., `*_pb2.py` and `*_pb2_grpc.py`) for gRPC communication.

## Dependencies and Setup

### Required Libraries

- **Python 3.8+**
- **Django**
- **gRPC Libraries:**
  - `grpcio`
  - `grpcio-tools`
- **Other Libraries:**
  - `requests` (if used for additional HTTP communications)

### Installation

Install the required libraries using pip:

```bash
pip install django grpcio grpcio-tools requests
```

### Running the Services

- 1. **Start the Django Application**:

```bash
python manage.py runserver
```

- 2. **Start the gRPC Callback Servers**:

```bash
python wallet_service/grpc/payment_callback_server.py
```

```bash
python wallet_service/grpc/refund_callback_server.py
```

## Summary

WalletService is designed to manage wallet transactions through asynchronous, gRPC-based interactions with external microservices. Its key operations include:

- **Credit Operations (PaymentGatewayService):**
  - Creating a **PENDING** credit transaction.
  - Sending the transaction details to PaymentGatewayService.
  - Receiving a callback to update the wallet balance when the transaction is completed.

- **Debit Operations (RefundService):**
  - Creating a **PENDING** debit (refund) transaction.
  - Sending the refund transaction details to RefundService.
  - Receiving a callback to subtract the refund amount from the wallet balance when the transaction is completed.

- **User Event Processing:**
  - Using the Observer pattern to trigger wallet creation when new user events are received.

By combining the Observer Pattern with gRPC client/server communication, WalletService achieves decoupled, scalable, and efficient processing of wallet transactions.