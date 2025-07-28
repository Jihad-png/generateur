import streamlit as st
from typing import List
from models import Client
import zipfile
from io import BytesIO

def create_download_button(clients: List[Client], pdf_generator):
    """Crée les boutons de téléchargement pour les factures"""
    
    if len(clients) == 1:
        # Un seul client - téléchargement direct
        client = clients[0]
        pdf_buffer = pdf_generator.generate_pdf(client)
        
        st.download_button(
            label=f"📄 Télécharger la facture de {client.name}",
            data=pdf_buffer.getvalue(),
            file_name=f"facture_globale_{client.name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    else:
        # Plusieurs clients - option ZIP
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Factures individuelles")
            for i, client in enumerate(clients):
                pdf_buffer = pdf_generator.generate_pdf(client)
                st.download_button(
                    label=f"Télécharger la facture de{client.number}",
                    data=pdf_buffer.getvalue(),
                    file_name=f"facture_globale_{client.number.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key=f"download_{i}",
                    use_container_width=True
                )
        
        with col2:
            st.subheader("📦 Téléchargement groupé")
            if st.button("Créer l'archive ZIP", use_container_width=True):
                zip_buffer = create_zip_archive(clients, pdf_generator)
                
                st.download_button(
                    label="🗂️ Télécharger toutes les factures (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="factures_globales.zip",
                    mime="application/zip",
                    use_container_width=True
                )

def create_zip_archive(clients: List[Client], pdf_generator) -> BytesIO:
    """Crée une archive ZIP avec toutes les factures"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for client in clients:
            pdf_buffer = pdf_generator.generate_pdf(client)
            filename = f"facture_globale_{client.name.replace(' ', '_')}.pdf"
            zip_file.writestr(filename, pdf_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer

def format_currency(amount) -> str:
    """Formate un montant en MAD"""
    return f"{amount:.2f} "

def validate_upload(uploaded_file) -> bool:
    """Valide le fichier uploadé"""
    if uploaded_file is None:
        return False
    
    # Vérifier l'extension
    allowed_extensions = ['.xlsx', '.xls']
    file_extension = uploaded_file.name.lower().split('.')[-1]
    
    return f".{file_extension}" in allowed_extensions

def show_sample_format():
    """Affiche le format attendu du fichier Excel"""
    st.subheader("📋 Format attendu du fichier Excel")
    
    sample_data = {
        'Numéro_client': ['C001', 'C001', 'C002'],
        'addresse_client': ['123 Rue A', '123 Rue A', '456 Rue B'],
        'Numéro_facture': ['F001', 'F002', 'F003'],
        'Numéro_contrat':['C001-001', 'C001-002', 'C002-001'],
        'montant_ht': [100.00, 200.00, 150.00],
        'montant_tva': [20.00, 40.00, 30.00],
        'date': ['2024-01-15', '2024-01-20', '2024-01-18'],
        
    }
    
    st.write("**Colonnes obligatoires :**")
    st.write("- `Numéro_client` : Numéro du client")
    st.write("- `client_address` : Adresse du client")
    st.write("- `invoice_number` : Numéro de facture")
    st.write("- `contrat_number` : Numéro de contrat")
    st.write("- `amount_ht` : Montant hors taxes")
    st.write("- `amount_tva` : Montant de la TVA")
    
    st.write("**Colonnes optionnelles :**")
    st.write("- `date` : Date de la facture")
    
    
    st.write("**Exemple de données :**")
    import pandas as pd
    st.dataframe(pd.DataFrame(sample_data), use_container_width=True)