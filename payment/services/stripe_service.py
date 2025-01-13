import stripe
from django.conf import settings
from payment.models import StripeCustomer

class StripeService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_customer(self, user, email, name):
        """
        Create a Stripe customer for a user
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            
            # Save Stripe customer ID to database
            StripeCustomer.objects.create(
                user=user,
                stripe_customer_id=customer.id
            )
            
            return customer
        except stripe.error.StripeError as e:
            # Handle Stripe errors
            return None

    def create_payment_intent(self, amount, currency='usd'):
        """
        Create a Stripe Payment Intent
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                payment_method_types=['card']
            )
            return intent
        except stripe.error.StripeError as e:
            # Handle Stripe errors
            return None

    def confirm_payment(self, payment_intent_id):
        """
        Confirm a Stripe payment
        """
        try:
            intent = stripe.PaymentIntent.confirm(payment_intent_id)
            return intent
        except stripe.error.StripeError as e:
            # Handle Stripe errors
            return None