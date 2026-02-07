import pandas as pd
import os
import numpy as np

class SwissGridLoader:
    def __init__(self, filepath_swissgrid, filepath_prices):
        self.filepath_swissgrid = filepath_swissgrid
        self.filepath_prices = filepath_prices

    def load_data(self):
        print(f"\n--- 1. CHARGEMENT SWISSGRID (Physique) ---")
        df = self._load_swissgrid_physical()
        if df is None: return None

        print(f"\n--- 2. CHARGEMENT PRIX SPOT (Financier) ---")
        df = self._merge_spot_prices(df)
        
        print(f"\n--- 3. CALCULS FINANCIERS ---")
        # On vérifie qu'on a bien des prix
        if df['Price_EUR'].sum() == 0:
            print("🛑 STOP : La colonne Prix est vide ou à 0. Le graphe sera vide.")
            # On continue quand même pour afficher les autres graphes
        else:
            # Formule
            df['Net_Revenue_EUR'] = (df['Export_Total_MW'] - df['Import_Total_MW']) * df['Price_EUR']
            df['Revenue_Cumul_Million_EUR'] = df['Net_Revenue_EUR'].cumsum() / 1_000_000
            
            last_val = df['Revenue_Cumul_Million_EUR'].iloc[-1]
            print(f"✅ CALCUL RÉUSSI. Bilan final : {last_val:.2f} Millions €")
        
        return df.dropna(subset=['Production_MW'])

    def _load_swissgrid_physical(self):
        print(f"Lecture Swissgrid : {self.filepath_swissgrid}")
        if not os.path.exists(self.filepath_swissgrid):
            raise FileNotFoundError(f"❌ Fichier Swissgrid introuvable : {self.filepath_swissgrid}")

        try:
            # Lecture
            df_raw = pd.read_excel(self.filepath_swissgrid, sheet_name='Zeitreihen0h15', header=0)
        except Exception as e:
            print(f"⚠️ Erreur lecture Excel : {e}")
            return None

        # Suppression ligne des unités (kWh) si présente
        if isinstance(df_raw.iloc[0, 2], str):
            df_raw = df_raw.drop(index=0)

        # Index Temporel
        df_raw.index = pd.to_datetime(df_raw.iloc[:, 0], dayfirst=True, errors='coerce')
        df_raw = df_raw[df_raw.index.notna()]
        # Gestion DST (Doublons changement d'heure)
        df_raw = df_raw[~df_raw.index.duplicated(keep='first')]

        # Conversion numérique globale
        df = df_raw.apply(pd.to_numeric, errors='coerce')

        print("Conversion kWh 15min -> MW Horaire...")
        
        # On prépare un nouveau DataFrame horaire pour éviter les problèmes d'index
        df_hourly = pd.DataFrame(index=df.resample('h').first().index)

        # --- A. Prod & Conso ---
        # Somme des 4 quarts d'heure / 1000
        df_hourly['Production_MW'] = df.iloc[:, 2].resample('h').sum() / 1000
        df_hourly['Consumption_MW'] = df.iloc[:, 3].resample('h').sum() / 1000
        
        # Gap (Charge Résiduelle)
        df_hourly['Residual_Load_MW'] = df_hourly['Consumption_MW'] - df_hourly['Production_MW']

        # --- B. Flux Frontières (Net Flow) ---
        neighbors = {'DE': 'DE', 'FR': 'FR', 'IT': 'IT', 'AT': 'AT'}
        for code in neighbors:
            col_e = next((c for c in df.columns if f"CH->{code}" in str(c)), None)
            col_i = next((c for c in df.columns if f"{code}->CH" in str(c)), None)
            if col_e and col_i:
                # Net = Export - Import
                net_flow = (df[col_e] - df[col_i]).resample('h').sum() / 1000
                df_hourly[f'Net_Flow_{code}_MW'] = net_flow

        # --- C. Flux Totaux ---
        col_imp = next((c for c in df.columns if "Import" in str(c).strip()), None)
        col_exp = next((c for c in df.columns if "Export" in str(c).strip()), None)
        
        if col_imp and col_exp:
            df_hourly['Import_Total_MW'] = df[col_imp].resample('h').sum() / 1000
            df_hourly['Export_Total_MW'] = df[col_exp].resample('h').sum() / 1000
            df_hourly['Total_Flux_MW'] = df_hourly['Import_Total_MW'] + df_hourly['Export_Total_MW']
        else:
            print("⚠️ Colonnes Import/Export introuvables !")
            return None

        # --- D. Transit ---
        col_transit = next((c for c in df.columns if "Transit" in str(c)), None)
        if col_transit:
            df_hourly['Transit_MW'] = df[col_transit].resample('h').sum() / 1000
        else:
            df_hourly['Transit_MW'] = 0

        return df_hourly.dropna(subset=['Production_MW'])

    def _merge_spot_prices(self, df_phys):
        print(f"--> Lecture Prix Spot : {self.filepath_prices}")
        
        if not os.path.exists(self.filepath_prices):
            print("⚠️ Fichier Prix introuvable. Prix mis à 0.")
            df_phys['Price_EUR'] = 0
            return df_phys

        try:
            # 1. TENTATIVE INTELLIGENTE
            try:
                df_price = pd.read_excel(self.filepath_prices)
            except:
                df_price = pd.read_csv(self.filepath_prices, sep=None, engine='python')

            # 2. COLONNE UNIQUE (format : YYYY-MM-DD,Price) -> NETTOYAGE DES DONNÉES
            col_name = df_price.columns[0]
            df_price = df_price.iloc[:, 0].astype(str).str.replace('"', '').str.split(',', expand=True)
            df_price.columns = ['Datum', 'Price']
            
            # Nettoyage des noms de colonnes
            df_price.columns = [c.strip().replace('"', '').replace("'", "") for c in df_price.columns]

            # 3. IDENTIFICATION COLONNES
            col_price = next((c for c in df_price.columns if 'Baseload' in c or 'Price' in c or 'EUR' in c), None)
            col_date = next((c for c in df_price.columns if 'Datum' in c or 'Date' in c), None)

            # 4. CONVERSION
            df_price['Datum'] = pd.to_datetime(df_price[col_date], errors='coerce')
            df_price['Price_EUR'] = pd.to_numeric(df_price[col_price], errors='coerce')
            df_price = df_price.dropna(subset=['Datum', 'Price_EUR'])

            # --- ON GARDE QUE 2025 ---
            year_phys = df_phys.index.year[0] # L'année cible (2025)
            df_target = df_price[df_price['Datum'].dt.year == year_phys].copy()

            # 5. FUSION (MERGE)
            df_phys['Join_Date'] = df_phys.index.normalize()
            df_price['Join_Date'] = df_price['Datum'].dt.normalize()
            
            # On ne garde que les colonnes utiles et on vire les doublons créés par le forcage
            df_clean_price = df_price[['Join_Date', 'Price_EUR']].drop_duplicates(subset=['Join_Date'])
            
            print(f"   -> {len(df_clean_price)} prix journaliers prêts à être fusionnés.")

            # Merge
            df_merged = df_phys.merge(df_clean_price, on='Join_Date', how='left')
            
            # Nettoyage final
            df_merged.index = df_phys.index
            
            # Remplissage des trous
            df_merged['Price_EUR'] = df_merged['Price_EUR'].fillna(method='ffill').fillna(method='bfill').fillna(0)
            
            return df_merged.drop(columns=['Join_Date'])

        except Exception as e:
            print(f"❌ CRASH LECTURE PRIX : {e}")
            import traceback
            traceback.print_exc()
            df_phys['Price_EUR'] = 0
            return df_phys