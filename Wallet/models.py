from django.db import models
from enum import Enum
import uuid


class TransactionType(Enum):
    CREDIT = 'credit'  # افزایش موجودی
    DEBIT = 'debit'    # کاهش موجودی


class Wallet(models.Model):
    wallet_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    national_code = models.CharField(max_length=10, unique=True)  # کد ملی کاربر
    balance = models.BigIntegerField(default=0)  # موجودی کیف پول (تومان)

    def __str__(self):
        return f"Wallet of {self.national_code}"


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, related_name='transactions', on_delete=models.CASCADE)  # ارتباط با کیف پول
    amount = models.BigIntegerField()  # مبلغ تراکنش (تومان)
    transaction_type = models.CharField(max_length=50, choices=[(tag, tag.value) for tag in TransactionType], default=TransactionType.CREDIT.value)  # نوع تراکنش
    timestamp = models.DateTimeField(auto_now_add=True)  # زمان انجام تراکنش
    description = models.TextField(blank=True, null=True)  # توضیحات (اختیاری)

    def __str__(self):
        return f"Transaction {self.id} - {self.transaction_type} - {self.amount} for {self.wallet.national_code}"