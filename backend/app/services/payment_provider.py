from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hmac
import hashlib
import json
import httpx

from app.config import settings


class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class PaymentCustomer:
    """Customer payment info"""
    customer_id: str
    email: str
    phone: str


@dataclass
class Payment:
    """Payment session response"""
    payment_id: str
    redirect_url: str
    status: PaymentStatusEnum
    created_at: datetime


class PaymentProvider(ABC):
    """Abstract payment provider"""

    @abstractmethod
    async def create_payment(
        self,
        order_id: str,
        amount: int,
        customer: PaymentCustomer,
        return_url: str,
    ) -> Payment:
        """Create payment session"""
        pass

    @abstractmethod
    async def verify_webhook(
        self,
        payload: Dict[str, Any],
        signature: str,
    ) -> bool:
        """Verify webhook authenticity"""
        pass

    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> PaymentStatusEnum:
        """Get payment status"""
        pass

    @abstractmethod
    async def refund_payment(self, payment_id: str, amount: int) -> bool:
        """Refund payment"""
        pass


class YandexKassaProvider(PaymentProvider):
    """Яндекс.Касса (YandexKassa) payment provider"""

    def __init__(self, shop_id: str, secret_key: str, test_mode: bool = True):
        self.shop_id = shop_id
        self.secret_key = secret_key
        self.test_mode = test_mode
        self.api_url = "https://payment.yandex.net/api/v3"

    async def create_payment(
        self,
        order_id: str,
        amount: int,
        customer: PaymentCustomer,
        return_url: str,
    ) -> Payment:
        """Create payment via Yandex.Kassa"""
        # Convert amount from cents to rubles
        amount_rubles = amount / 100

        payload = {
            "amount": {
                "value": f"{amount_rubles:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": f"Order #{order_id}",
            "metadata": {
                "order_id": order_id
            },
            "test": self.test_mode
        }

        if customer.email:
            payload["receipt"] = {
                "customer": {"email": customer.email},
                "items": []
            }

        headers = {
            "Idempotence-Key": order_id,
            "Content-Type": "application/json"
        }

        # Basic auth with shop_id
        auth = (self.shop_id, self.secret_key)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/payments",
                json=payload,
                headers=headers,
                auth=auth,
                timeout=10.0
            )

            if response.status_code not in [200, 201]:
                raise Exception(f"Yandex.Kassa error: {response.text}")

            data = response.json()
            return Payment(
                payment_id=data["id"],
                redirect_url=data["confirmation"]["confirmation_url"],
                status=PaymentStatusEnum.PENDING,
                created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            )

    async def verify_webhook(
        self,
        payload: Dict[str, Any],
        signature: str,
    ) -> bool:
        """Verify webhook signature from Yandex.Kassa"""
        # Serialize data for signature
        data_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        expected_signature = hashlib.sha256(
            (data_str + self.secret_key).encode()
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    async def get_payment_status(self, payment_id: str) -> PaymentStatusEnum:
        """Get payment status from Yandex.Kassa"""
        auth = (self.shop_id, self.secret_key)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/payments/{payment_id}",
                auth=auth,
                timeout=10.0
            )

            if response.status_code != 200:
                raise Exception(f"Yandex.Kassa error: {response.text}")

            data = response.json()
            status = data.get("status")

            if status == "succeeded":
                return PaymentStatusEnum.PAID
            elif status == "canceled":
                return PaymentStatusEnum.FAILED
            else:
                return PaymentStatusEnum.PENDING

    async def refund_payment(self, payment_id: str, amount: int) -> bool:
        """Refund payment via Yandex.Kassa"""
        amount_rubles = amount / 100
        payload = {
            "amount": {
                "value": f"{amount_rubles:.2f}",
                "currency": "RUB"
            }
        }

        auth = (self.shop_id, self.secret_key)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/payments/{payment_id}/refunds",
                json=payload,
                auth=auth,
                timeout=10.0
            )

            return response.status_code in [200, 201]


class YuKassaProvider(PaymentProvider):
    """ЮKassa payment provider"""

    def __init__(self, merchant_id: str, secret_key: str, test_mode: bool = True):
        self.merchant_id = merchant_id
        self.secret_key = secret_key
        self.test_mode = test_mode
        self.api_url = "https://api.yukassa.ru/v1"

    async def create_payment(
        self,
        order_id: str,
        amount: int,
        customer: PaymentCustomer,
        return_url: str,
    ) -> Payment:
        """Create payment via ЮKassa"""
        amount_rubles = amount / 100

        payload = {
            "amount": int(amount),
            "currency": "RUB",
            "orderId": order_id,
            "description": f"Order #{order_id}",
            "returnUrl": return_url,
            "test": self.test_mode,
            "customerEmail": customer.email
        }

        headers = {
            "Content-Type": "application/json",
            "Merchant": self.merchant_id
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/payments/create",
                json=payload,
                headers=headers,
                timeout=10.0
            )

            if response.status_code != 200:
                raise Exception(f"ЮKassa error: {response.text}")

            data = response.json()
            return Payment(
                payment_id=data["paymentId"],
                redirect_url=data["redirectUrl"],
                status=PaymentStatusEnum.PENDING,
                created_at=datetime.utcnow()
            )

    async def verify_webhook(
        self,
        payload: Dict[str, Any],
        signature: str,
    ) -> bool:
        """Verify webhook signature from ЮKassa"""
        # Simple verification - implement based on actual API docs
        data_str = json.dumps(payload, sort_keys=True)
        expected_signature = hashlib.sha256(
            (data_str + self.secret_key).encode()
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    async def get_payment_status(self, payment_id: str) -> PaymentStatusEnum:
        """Get payment status from ЮKassa"""
        headers = {
            "Merchant": self.merchant_id,
            "Authorization": f"Bearer {self.secret_key}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/payments/{payment_id}",
                headers=headers,
                timeout=10.0
            )

            if response.status_code != 200:
                raise Exception(f"ЮKassa error: {response.text}")

            data = response.json()
            status = data.get("status")

            if status == "completed":
                return PaymentStatusEnum.PAID
            elif status in ["failed", "cancelled"]:
                return PaymentStatusEnum.FAILED
            else:
                return PaymentStatusEnum.PENDING

    async def refund_payment(self, payment_id: str, amount: int) -> bool:
        """Refund payment via ЮKassa"""
        payload = {
            "amount": amount,
            "paymentId": payment_id
        }

        headers = {
            "Content-Type": "application/json",
            "Merchant": self.merchant_id
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/payments/refund",
                json=payload,
                headers=headers,
                timeout=10.0
            )

            return response.status_code == 200


class SberPayProvider(PaymentProvider):
    """SberPay payment provider"""

    def __init__(self, merchant_id: str, secret_key: str, test_mode: bool = True):
        self.merchant_id = merchant_id
        self.secret_key = secret_key
        self.test_mode = test_mode
        self.api_url = "https://api.sber.ru/api/v1"

    async def create_payment(
        self,
        order_id: str,
        amount: int,
        customer: PaymentCustomer,
        return_url: str,
    ) -> Payment:
        """Create payment via SberPay"""
        payload = {
            "orderNumber": order_id,
            "amount": amount,
            "currency": "RUB",
            "returnUrl": return_url,
            "merchantLogin": self.merchant_id,
            "description": f"Order #{order_id}"
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.secret_key}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/payments",
                json=payload,
                headers=headers,
                timeout=10.0
            )

            if response.status_code not in [200, 201]:
                raise Exception(f"SberPay error: {response.text}")

            data = response.json()
            return Payment(
                payment_id=data["id"],
                redirect_url=data["redirectUrl"],
                status=PaymentStatusEnum.PENDING,
                created_at=datetime.utcnow()
            )

    async def verify_webhook(
        self,
        payload: Dict[str, Any],
        signature: str,
    ) -> bool:
        """Verify webhook signature from SberPay"""
        data_str = json.dumps(payload, sort_keys=True)
        expected_signature = hashlib.sha256(
            (data_str + self.secret_key).encode()
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    async def get_payment_status(self, payment_id: str) -> PaymentStatusEnum:
        """Get payment status from SberPay"""
        headers = {
            "Authorization": f"Bearer {self.secret_key}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/payments/{payment_id}",
                headers=headers,
                timeout=10.0
            )

            if response.status_code != 200:
                raise Exception(f"SberPay error: {response.text}")

            data = response.json()
            status = data.get("status")

            if status == "completed":
                return PaymentStatusEnum.PAID
            elif status in ["failed", "declined"]:
                return PaymentStatusEnum.FAILED
            else:
                return PaymentStatusEnum.PENDING

    async def refund_payment(self, payment_id: str, amount: int) -> bool:
        """Refund payment via SberPay"""
        payload = {
            "paymentId": payment_id,
            "amount": amount
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.secret_key}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/payments/{payment_id}/refund",
                json=payload,
                headers=headers,
                timeout=10.0
            )

            return response.status_code == 200


def get_payment_provider(provider_name: str, organization_data: Dict[str, Any]) -> PaymentProvider:
    """Factory function to get payment provider instance"""

    if provider_name == "yandex_kassa":
        return YandexKassaProvider(
            shop_id=settings.yandex_kassa_shop_id or "test_shop",
            secret_key=settings.yandex_kassa_secret_key or "test_secret",
            test_mode=settings.environment == "development"
        )
    elif provider_name == "yukassa":
        return YuKassaProvider(
            merchant_id=settings.yukassa_merchant_id or "test_merchant",
            secret_key=settings.yukassa_secret_key or "test_secret",
            test_mode=settings.environment == "development"
        )
    elif provider_name == "sberpay":
        return SberPayProvider(
            merchant_id=settings.sberpay_merchant_id or "test_merchant",
            secret_key=settings.sberpay_secret_key or "test_secret",
            test_mode=settings.environment == "development"
        )
    else:
        raise ValueError(f"Unknown payment provider: {provider_name}")
