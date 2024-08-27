from datetime import datetime
from enum import Enum

from pydantic import BaseModel, computed_field, model_validator
from typing_extensions import Optional, Self


class Location(BaseModel):
    address: str
    latitude: float
    longitude: float
    postalcode: Optional[str]


class Sender(BaseModel):
    name: Optional[str]
    phone_number: Optional[str]
    location: Optional[Location]
    notes: Optional[str]
    client_vendor_id: Optional[str]

    @model_validator(mode="after")
    def check_sender_information(self) -> Self:
        if self.client_vendor_id is None:
            if self.name is None or self.phone_number is None or self.location is None:
                raise ValueError(
                    "Either client_vendor_id or name, phone_number, and location must be provided"
                )
        return self


class Recipient(BaseModel):
    name: str
    phone_number: str
    location: Location
    notes: Optional[str]


class Driver(BaseModel):
    id: str
    name: str
    phone_number: str


class PaymentMethod(str, Enum):
    PAID = "PAID"
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY"


class DeliveryTasks(BaseModel):
    age_verification_required: bool


class OrderInput(BaseModel):
    client_order_id: Optional[str]
    sender: Optional[Sender]
    recipient: Recipient
    payment_method: Optional[PaymentMethod]
    amount: float
    collect_from_customer: Optional[float]
    coldbag_needed: Optional[bool]
    description: str
    preordered_for: Optional[int]
    delivery_tasks: Optional[DeliveryTasks]


class OrderStatus(str, Enum):
    NEW = "NEW"
    RECEIVED = "RECEIVED"
    WAITING_FOR_TRANSPORT = "WAITING_FOR_TRANSPORT"
    ASSIGNED_TO_TRANSPORT = "ASSIGNED_TO_TRANSPORT"
    COURIER_ACCEPTED_DELIVERY = "COURIER_ACCEPTED_DELIVERY"
    NEAR_VENDOR = "NEAR_VENDOR"
    PICKED_UP = "PICKED_UP"
    COURIER_LEFT_VENDOR = "COURIER_LEFT_VENDOR"
    NEAR_CUSTOMER = "NEAR_CUSTOMER"
    DELIVERED = "DELIVERED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"
    RETURNED_TO_VENDOR = "RETURNED_TO_VENDOR"


class OrderTimeline(BaseModel):
    estimated_pickup_time: str
    estimated_delivery_time: str


class CancellationSource(str, Enum):
    CLIENT = "CLIENT"
    LOGISITICS = "LOGISTICS"


class CancellationReason(str, Enum):
    ADDRESS_INCOMPLETE_MISSTATED = "ADDRESS_INCOMPLETE_MISSTATED"
    BAD_WEATHER = "BAD_WEATHER"
    CLOSED = "CLOSED"
    COURIER_ACCIDENT = "COURIER_ACCIDENT"
    COURIER_UNREACHABLE = "COURIER_UNREACHABLE"
    DELIVERY_ETA_TOO_LONG = "DELIVERY_ETA_TOO_LONG"
    DUPLICATE_ORDER = "DUPLICATE_ORDER"
    FOOD_QUALITY_SPILLAGE = "FOOD_QUALITY_SPILLAGE"
    LATE_DELIVERY = "LATE_DELIVERY"
    MISTAKE_ERROR = "MISTAKE_ERROR"
    NO_COURIER = "NO_COURIER"
    OUTSIDE_DELIVERY_AREA = "OUTSIDE_DELIVERY_AREA"
    OUTSIDE_SERVICE_HOURS = "OUTSIDE_SERVICE_HOURS"
    REASON_UNKNOWN = "REASON_UNKNOWN"
    TECHNICAL_PROBLEM = "TECHNICAL_PROBLEM"
    UNABLE_TO_FIND = "UNABLE_TO_FIND"
    UNABLE_TO_PAY = "UNABLE_TO_PAY"
    WRONG_ORDER_ITEMS_DELIVERED = "WRONG_ORDER_ITEMS_DELIVERED"


class Cancellation(BaseModel):
    source: CancellationSource
    reason: CancellationReason


class Order(BaseModel):
    order_id: str
    client_order_id: str
    sender: Sender
    recipient: Recipient
    distance: float
    payment_method: PaymentMethod
    coldbag_needed: bool
    amount: float
    description: str
    status: OrderStatus
    delivery_fee: float
    timeline: OrderTimeline
    driver: Driver
    created_at: datetime
    updated_at: datetime
    delivery_tasks: DeliveryTasks

    # Detailed Response fields
    is_dynamic_pickup: Optional[bool]
    tracking_link: Optional[str]
    proof_of_delivery_url: Optional[str]
    proof_of_pickup_url: Optional[str]
    proof_of_return_url: Optional[str]
    cancellation: Optional[Cancellation]

    @computed_field
    def is_detailed(self) -> bool:
        return (
            self.tracking_link is not None
            or self.proof_of_pickup_url is not None
            or self.proof_of_delivery_url is not None
            or self.proof_of_return_url is not None
            or self.cancellation is not None
            or self.is_dynamic_pickup is not None
        )


class OrderCancellationInput(BaseModel):
    reason: CancellationReason

    @model_validator(mode="after")
    def check_valid_reason(self) -> Self:
        if self.reason not in [
            CancellationReason.DELIVERY_ETA_TOO_LONG,
            CancellationReason.MISTAKE_ERROR,
            CancellationReason.REASON_UNKNOWN,
        ]:
            raise ValueError(
                "Invalid Cancellation Reason. Consult https://pandago.docs.apiary.io/#reference/orders/operation/cancel-specific-order for valid reasons."
            )
        return self


class UpdateOrderLocationInput(BaseModel):
    address: Optional[str]
    latitude: float
    longitude: float
    notes: Optional[str]


class UpdateOrderInput(BaseModel):
    payment_method: Optional[PaymentMethod]
    amount: Optional[float]
    location: Optional[UpdateOrderLocationInput]
    description: Optional[str]
