import pandas as pd
import os

class SwissGridLoader:
    def __init__(self, filepath):
        self.filepath = filepath

    def load_data(self):
        print(f"Lecture du fichier (Mode Complet) : {self.filepath}")
        
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"❌ Fichier introuvable : {self.filepath}")

        try:
            # Lecture avec header=0 (ligne 1)
            df_raw = pd.read_excel(self.filepath, sheet_name='Zeitreihen0h15', header=0)
        except Exception as e:
            print(f"⚠️ Erreur lecture Excel : {e}")
            return None

        # Suppression ligne des unités (kWh)
        if isinstance(df_raw.iloc[0, 2], str):
            df_raw = df_raw.drop(index=0)

        # 1. Gestion des Dates
        dates = pd.to_datetime(df_raw.iloc[:, 0], dayfirst=True, errors='coerce')
        df_raw.index = dates
        
        # Nettoyage
        df_raw = df_raw[df_raw.index.notna()]
        if df_raw.index.duplicated().any():
            print("⚠️ Correction doublons temporels (DST).")
            df_raw = df_raw[~df_raw.index.duplicated(keep='first')]

        # 2. Conversion Numérique
        df = df_raw.apply(pd.to_numeric, errors='coerce')

        print("Calcul centralisé des puissances (Conversion kWh 15min -> MW Horaire)...")
        
        # --- A. PRODUCTION & CONSOMMATION ---
        df['Production_MW'] = df.iloc[:, 2].resample('h').sum() / 1000
        df['Consumption_MW'] = df.iloc[:, 3].resample('h').sum() / 1000

        # --- B. FLUX PAR FRONTIÈRE (Calcul Net MW) ---
        # On calcule le solde net (Export - Import) pour chaque voisin directement ici
        neighbors = {'DE': 'DE', 'FR': 'FR', 'IT': 'IT', 'AT': 'AT'}

        for code in neighbors:
            # Recherche des colonnes brutes (kWh)
            col_exp = next((c for c in df.columns if f"CH->{code}" in str(c)), None)
            col_imp = next((c for c in df.columns if f"{code}->CH" in str(c)), None)
            
            if col_exp and col_imp:
                # Calcul : Net = Export - Import
                # Formule : Somme des kWh 15min sur 1h / 1000 = MW moyen
                net_kwh_15min = df[col_exp] - df[col_imp]
                df[f'Net_Flow_{code}_MW'] = net_kwh_15min.resample('h').sum() / 1000

        # --- C. FLUX TOTAUX ---
        col_import = next((c for c in df.columns if str(c).strip() == "Import"), None)
        col_export = next((c for c in df.columns if str(c).strip() == "Export"), None)

        df['Import_Total_MW'] = df[col_import].resample('h').sum() / 1000
        df['Export_Total_MW'] = df[col_export].resample('h').sum() / 1000
        df['Total_Flux_MW'] = df['Import_Total_MW'] + df['Export_Total_MW']

        # --- D. TRANSIT ---
        col_transit = next((c for c in df.columns if str(c).strip() == "Transit"), None)
        if col_transit:
            df['Transit_MW'] = df[col_transit].resample('h').sum() / 1000
        else:
            df['Transit_MW'] = 0

        return df.dropna(subset=['Production_MW', 'Consumption_MW'])