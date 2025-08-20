from dataclasses import dataclass
from typing import Protocol, Tuple

from src.core.config import get_settings

settings = get_settings()


class PaymentError(Exception):
    pass


class PaymentProvider(Protocol):
    # PUBLIC_INTERFACE
    def charge(self, amount_cents: int, currency: str, token: str) -> Tuple[str, str]:
        """Charge the specified amount and return (status, provider_ref)."""


@dataclass
class StripeProvider:
    api_key: str | None = None

    # PUBLIC_INTERFACE
    def charge(self, amount_cents: int, currency: str, token: str) -> Tuple[str, str]:
        """Simulate Stripe charge; accepts tokens starting with 'tok_' as success."""
        if not token.startswith("tok_"):
            return ("failed", "")
        provider_ref = f"pi_{token[-10:]}"
        return ("succeeded", provider_ref)


@dataclass
class PayPalProvider:
    client_id: str | None = None
    client_secret: str | None = None

    # PUBLIC_INTERFACE
    def charge(self, amount_cents: int, currency: str, token: str) -> Tuple[str, str]:
        """Simulate PayPal capture; tokens starting with 'pp_' succeed."""
        if not token.startswith("pp_"):
            return ("failed", "")
        provider_ref = f"pp_txn_{token[-10:]}"
        return ("succeeded", provider_ref)


@dataclass
class MockUPIProvider:
    # PUBLIC_INTERFACE
    def charge(self, amount_cents: int, currency: str, token: str) -> Tuple[str, str]:
        """Simulate UPI payment; tokens starting with 'upi_' succeed."""
        if not token.startswith("upi_"):
            return ("failed", "")
        provider_ref = f"upi_txn_{token[-10:]}"
        return ("succeeded", provider_ref)


# PUBLIC_INTERFACE
def get_payment_provider(name: str) -> PaymentProvider:
    """Factory to get a payment provider by name."""
    n = name.lower()
    if n == "stripe":
        return StripeProvider(api_key=settings.STRIPE_API_KEY)
    if n == "paypal":
        return PayPalProvider(client_id=settings.PAYPAL_CLIENT_ID, client_secret=settings.PAYPAL_CLIENT_SECRET)
    if n == "upi":
        return MockUPIProvider()
    raise PaymentError(f"Unsupported payment provider: {name}")
