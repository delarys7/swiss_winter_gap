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
        df_raw = df_raw.drop(index=0)

        # 1. Gestion des Dates
        dates = pd.to_datetime(df_raw.iloc[:, 0], dayfirst=True)
        df_raw.index = dates
        
        # 2. On garde une copie propre pour travailler
        # On force la conversion en numérique pour tout le monde (sinon c'est du texte)
        df = df_raw.apply(pd.to_numeric, errors='coerce')

        # 3. On recrée nos colonnes standards (pour que le code Winter Gap continue de marcher)
        # Prod = Col C (index 2), Conso = Col D (index 3)
        print("Calcul des puissances globales (MW)...")
        # .resample('h').sum() / 1000 : On passe de kWh/15min à MW moyen horaire
        df['Production_MW'] = df.iloc[:, 2].resample('h').sum() / 1000
        df['Consumption_MW'] = df.iloc[:, 3].resample('h').sum() / 1000
        
        # Le reste des colonnes (les frontières) reste disponible dans 'df'
        # mais elles sont encore en format "kWh 15min", le border_analyzer s'occupera de les convertir.
        
        return df.dropna(subset=['Production_MW', 'Consumption_MW'])