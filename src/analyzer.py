import pandas as pd

class WinterGapAnalyzer:
    def __init__(self, df):
        self.df = df

    def analyze(self):
        """Calcule la Position Nette (Export vs Import)"""
        
        # Net Position : Positif = Export, Négatif = Import
        self.df['Net_Position_MW'] = self.df['Production_MW'] - self.df['Consumption_MW']
        
        # Calcul des KPIs pour affichage console
        max_deficit = self.df['Net_Position_MW'].min()
        hours_import = len(self.df[self.df['Net_Position_MW'] < 0])
        total_import_need = self.df[self.df['Net_Position_MW'] < 0]['Net_Position_MW'].sum()
        
        print(f"\n--- RÉSULTATS DE L'ANALYSE (Suisse {self.df.index.year.unique()[0]}) ---")
        print(f"Déficit Hivernal Max (Pointe) : {max_deficit:.2f} MW")
        print(f"Heures d'import nécessaire    : {hours_import} h / 8760 h")
        print(f"Volume total à importer       : {abs(total_import_need)/1000:.2f} GWh")
        print(f"---------------------------------------------------\n")
        
        return self.df