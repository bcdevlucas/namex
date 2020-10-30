from .abstract import Serializable
from dataclasses import dataclass
from datetime import date


@dataclass
class PaymentInfo(Serializable):
    methodOfPayment: str


@dataclass
class FilingInfo(Serializable):
    corpType: str
    date: date
    filingTypes: list


@dataclass
class FilingType(Serializable):
    filingTypeCode: str
    priority: str
    filingTypeDescription: str


@dataclass
class ContactInfo(Serializable):
    firstName: str
    lastName: str
    address: str
    city: str
    province: str
    postalCode: str


@dataclass
class BusinessInfo(Serializable):
    businessIdentifier: str
    businessName: str
    contactInfo: ContactInfo


@dataclass
class PaymentRequest(Serializable):
    """
    Sample request:
    {
        "paymentInfo": {
            "methodOfPayment": "CC"
        },
        "businessInfo": {
            "businessIdentifier": "CP1234567",
            "corpType": "NRO",
            "businessName": "ABC Corp",
            "contactInfo": {
                "city": "Victoria",
                "postalCode": "V8P2P2",
                "province": "BC",
                "addressLine1": "100 Douglas Street",
                "country": "CA"
            }
        },
        "filingInfo": {
            "filingTypes": [
                {
                    "filingTypeCode": "ABC",
                    "filingDescription": "TEST"
                },
                {
                    "filingTypeCode": "ABC"
                    ...
                }
            ]
        }
    }
    """
    paymentInfo: PaymentInfo
    filingInfo: FilingInfo
    businessInfo: BusinessInfo


@dataclass
class Payment(Serializable):
    id: int
    paymentMethod: str
    businessIdentifier: str
    corpTypeCode: str
    lineItems: list
    serviceFees: float
    paid: float
    refund: float
    total: float
    references: list
    statusCode: str
    createdBy: str
    createdName: str
    createdOn: str
    _links: list
