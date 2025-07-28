from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal

@dataclass
class Invoice:
    """Représente une facture individuelle"""
    invoice_number: str
    client_number: str
    client_address: str
    contrat_number:str
    amount_ht: Decimal
    amount_tva: Decimal
    amount_ttc: Decimal
    date: Optional[str] = None
    

@dataclass
class Client:
    """Représente un client avec ses factures groupées"""
    number: str
    address: str
    invoices: List[Invoice]
    total_ht: Decimal
    total_tva: Decimal
    total_ttc: Decimal

@dataclass
class Company:
    """Informations de l'entreprise"""
    name: str = "SRM-SM"
    address: str = "Rue 18 Novembre Quartier Industriel AGADIR"
    phone: str = "05 28 82 96 00 "
    email: str = "Contact@srm-sm.ma"
    logo_path: str = "assets/logo.jpg"