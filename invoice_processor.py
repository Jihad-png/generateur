import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple
from models import Invoice, Client
import streamlit as st

class InvoiceProcessor:
    """Traite les factures Excel et les regroupe par client"""
    
    def __init__(self):
        self.required_columns = [
            'Numéro_client', 'addresse_client','Numéro_contrat' , 'Numéro_facture', 
            'montant_ht', 'montant_tva'
        ]
    
    def validate_excel_structure(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """Valide la structure du fichier Excel"""
        try:
            # Vérifier les colonnes requises
            missing_columns = [col for col in self.required_columns if col not in df.columns]
            if missing_columns:
                return False, f"Colonnes manquantes : {', '.join(missing_columns)}"
            
            # Vérifier que le DataFrame n'est pas vide
            if df.empty:
                return False, "Le fichier Excel est vide"
            
            # Vérifier les types de données
            numeric_columns = ['montant_ht', 'montant_tva']
            for col in numeric_columns:
                try:
                    pd.to_numeric(df[col], errors='raise')
                except (ValueError, TypeError):
                    return False, f"La colonne '{col}' doit contenir uniquement des nombres"
            
            return True, "Structure valide"
        
        except Exception as e:
            return False, f"Erreur lors de la validation : {str(e)}"
    
    def clean_decimal(self, value) -> Decimal:
        """Nettoie et convertit une valeur en Decimal"""
        if pd.isna(value):
            return Decimal('0.00')
        
        # Convertir en string et nettoyer
        str_value = str(value).strip()
        
        # Remplacer les virgules par des points pour les décimaux
        str_value = str_value.replace(',', '.')
        
        try:
            return Decimal(str_value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except:
            return Decimal('0.00')
    
    def process_excel_file(self, uploaded_file) -> Tuple[bool, List[Client], str]:
        """Traite le fichier Excel et retourne les clients groupés"""
        try:
            # Lire le fichier Excel
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            # Valider la structure
            is_valid, message = self.validate_excel_structure(df)
            if not is_valid:
                return False, [], message
            
            # Nettoyer les données
            df = df.dropna(subset=['Numéro_client', 'Numéro_facture','Numéro_contrat'])
            df['Numéro_client'] = df['Numéro_client'].astype(str).str.strip()
            df['addresse_client'] = df['addresse_client'].fillna('').astype(str).str.strip()
            df['Numéro_facture'] = df['Numéro_facture'].astype(str).str.strip()
            df['Numéro_contrat'] = df['Numéro_contrat'].astype(str).str.strip()
            
            # Convertir les montants
            df['montant_ht'] = df['montant_ht'].apply(self.clean_decimal)
            df['montant_tva'] = df['montant_tva'].apply(self.clean_decimal)
            
            # Calculer le TTC
            df['montant_ttc'] = df['montant_ht'] + df['montant_tva']
            
            # Créer les objets Invoice
            invoices = []
            for _, row in df.iterrows():
                invoice = Invoice(
                    invoice_number=row['Numéro_facture'],
                    client_number=row['Numéro_client'],
                    client_address=row['addresse_client'],
                    contrat_number=row['Numéro_contrat'],
                    amount_ht=row['montant_ht'],
                    amount_tva=row['montant_tva'],
                    amount_ttc=row['montant_ttc'],
                    date=row.get('date', ''),
                    
                )
                invoices.append(invoice)
            
            # Grouper par client
            clients = self.group_by_client(invoices)
            
            return True, clients, f"Traitement réussi : {len(clients)} clients trouvés"
        
        except Exception as e:
            return False, [], f"Erreur lors du traitement : {str(e)}"
    
    def group_by_client(self, invoices: List[Invoice]) -> List[Client]:
        """Groupe les factures par client"""
        clients_dict: Dict[str, List[Invoice]] = {}
        
        # Grouper les factures par numéro de client
        for invoice in invoices:
            client_key = invoice.client_number.lower().strip()
            if client_key not in clients_dict:
                clients_dict[client_key] = []
            clients_dict[client_key].append(invoice)
        
        # Créer les objets Client
        clients = []
        for client_invoices in clients_dict.values():
            # Prendre l'adresse de la première facture pour le client
            client_number = client_invoices[0].client_number
            client_address = client_invoices[0].client_address
            
            # Calculer les totaux
            total_ht = sum(inv.amount_ht for inv in client_invoices)
            total_tva = sum(inv.amount_tva for inv in client_invoices)
            total_ttc = total_ht + total_tva
            
            client = Client(
                number=client_number,
                address=client_address,
                invoices=client_invoices,
                total_ht=total_ht,
                total_tva=total_tva,
                total_ttc=total_ttc
            )
            clients.append(client)
        
        # Trier par nom de client
        clients.sort(key=lambda c: c.number.lower())
        
        return clients
    
    def get_summary_dataframe(self, clients: List[Client]) -> pd.DataFrame:
        """Crée un DataFrame résumé pour affichage"""
        data = []
        for client in clients:
            data.append({
                'Client': client.number,
                'Nb Factures': len(client.invoices),
                'Total HT ': f"{client.total_ht:.2f}",
                'Total TVA ': f"{client.total_tva:.2f}",
                'Total TTC ': f"{client.total_ttc:.2f}"
            })
        
        return pd.DataFrame(data)