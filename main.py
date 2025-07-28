import streamlit as st
import pandas as pd
from invoice_processor import InvoiceProcessor
from pdf_generator import PDFGenerator
from models import Company
from utils import create_download_button, validate_upload, show_sample_format
import os

# Configuration de la page
st.set_page_config(
    page_title="Générateur de Factures",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2980b9 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }
    
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #721c24;
    }
    
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #0c5460;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f4e79;
        margin-bottom: 1rem;
    }
    
    .stDataFrame {
        border: 2px solid #e9ecef;
        border-radius: 8px;
    }
    
    .upload-box {
        border: 2px dashed #1f4e79;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>🧾 Générateur de Factures Globales</h1>
        <p>Générez automatiquement des factures PDF groupées par client </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialisation
    processor = InvoiceProcessor()
    company = Company()
    pdf_generator = PDFGenerator(company)
    
    # Sidebar pour les paramètres
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Configuration de l'entreprise
        with st.expander("🏢 Informations Entreprise", expanded=False):
            company.name = st.text_input("Nom de l'entreprise", value=company.name)
            company.address = st.text_area("Adresse", value=company.address, height=80)
            company.phone = st.text_input("Téléphone", value=company.phone)
            company.email = st.text_input("Email", value=company.email)
        
        # Aide et documentation
        st.markdown("---")
        st.header("📚 Aide")
        
        if st.button("📋 Voir le format Excel", use_container_width=True):
            st.session_state.show_format = True
        
        st.markdown("""
        **Instructions :**
        1. Uploadez votre fichier Excel
        2. Vérifiez l'aperçu des données
        3. Téléchargez les factures PDF
        
        **Format requis :**
        - Colonnes obligatoires : Numéro_client,
                    addresse_client,
                    Numéro_contrat,
                    Numéro_facture,
                    montant_ht,
                    montant_tva
        - Format : Excel (.xlsx, .xls)
        """)
    
    # Interface principale
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📤 Upload du fichier Excel")
        
        # Zone d'upload
        uploaded_file = st.file_uploader(
            "",
            type=['xlsx', 'xls'],
            help="Sélectionnez un fichier Excel contenant les données des factures"
        )
        
        if uploaded_file is not None:
            if validate_upload(uploaded_file):
                # Traitement du fichier
                with st.spinner("Traitement du fichier en cours..."):
                    success, clients, message = processor.process_excel_file(uploaded_file)
                
                if success:
                    # Message de succès
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>✅ Succès :</strong> {message}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Métriques
                    st.subheader("📊 Résumé")
                    col1_metrics, col2_metrics, col3_metrics = st.columns(3)
                    
                    total_invoices = sum(len(client.invoices) for client in clients)
                    total_amount = sum(client.total_ttc for client in clients)
                    
                    with col1_metrics:
                        st.metric("Clients", len(clients))
                    
                    with col2_metrics:
                        st.metric("Factures", total_invoices)
                    
                    with col3_metrics:
                        st.metric("Montant total TTC", f"{total_amount:.2f} ")
                    
                    # Tableau récapitulatif
                    st.subheader("📋 Aperçu des clients")
                    summary_df = processor.get_summary_dataframe(clients)
                    st.dataframe(summary_df, use_container_width=True)
                    
                    # Détails par client
                    st.subheader("🔍 Détails par client")
                    
                    for i, client in enumerate(clients):
                        with st.expander(f"📄 {client.number} - {len(client.invoices)} facture(s) - {client.total_ttc:.2f} "):
                            
                            col_info, col_invoices = st.columns([1, 2])
                            
                            with col_info:
                                st.write("**Adresse :**")
                                st.write(client.address)
                                
                                st.write("**Totaux :**")
                                st.write(f"HT : {client.total_ht:.2f} ")
                                st.write(f"TVA : {client.total_tva:.2f} ")
                                st.write(f"TTC : {client.total_ttc:.2f} ")
                            
                            with col_invoices:
                                invoice_data = []
                                for inv in client.invoices:
                                    invoice_data.append({
                                        'N° Facture': inv.invoice_number,
                                        'HT ': f"{inv.amount_ht:.2f}",
                                        'TVA ': f"{inv.amount_tva:.2f}",
                                        'TTC ': f"{inv.amount_ttc:.2f}"
                                    })
                                
                                st.dataframe(pd.DataFrame(invoice_data), use_container_width=True)
                    
                    # Section de téléchargement
                    st.markdown("---")
                    st.header("📥 Téléchargement des factures")
                    create_download_button(clients, pdf_generator)
                
                else:
                    # Message d'erreur
                    st.markdown(f"""
                    <div class="error-box">
                        <strong>❌ Erreur :</strong> {message}
                    </div>
                    """, unsafe_allow_html=True)
            
            else:
                st.error("Format de fichier non supporté. Veuillez utiliser un fichier Excel (.xlsx, .xls)")
        
        else:
            st.markdown("""
            <div class="upload-box">
                <h3>📁 Glissez-déposez votre fichier Excel ici</h3>
                <p>ou cliquez sur "Browse files" pour sélectionner votre fichier</p>
                <p><small>Formats supportés : .xlsx, .xls</small></p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.header("ℹ️ Informations")
        
        st.markdown("""
        <div class="info-box">
            <h4>🎯 Fonctionnalités</h4>
            <ul>
                <li>Groupement automatique par client</li>
                <li>Calculs automatiques HT/TVA/TTC</li>
                <li>Génération PDF professionnelle</li>
                <li>Téléchargement individuel ou groupé</li>
                <li>Validation des données</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        
        st.markdown("""
        <div class="info-box">
            <h4>📐 Formule de calcul</h4>
            <p><strong>TTC = HT + TVA</strong></p>
            <p>Le montant TTC est calculé en additionnant tous les montants HT et tous les montants de TVA de chaque facture du client.</p>
        </div>
        """, unsafe_allow_html=True)
        
    
    # Affichage du format si demandé
    if st.session_state.get('show_format', False):
        st.markdown("---")
        show_sample_format()
        
        if st.button("Masquer le format"):
            st.session_state.show_format = False

if __name__ == "__main__":
    main()