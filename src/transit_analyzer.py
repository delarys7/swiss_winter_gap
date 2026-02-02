import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class TransitAnalyzer:
    def __init__(self, df):
        self.df = df

    def _prepare_data(self):
        """Prépare toutes les métriques (Flux Total, Transit Pur, Conso)"""
        # Récupération des colonnes frontières
        cols_borders = [c for c in self.df.columns if "Verbundaustausch" in str(c)]
        
        if not cols_borders:
            print("⚠️ Erreur: Colonnes frontières introuvables.")
            return None

        # Séparation Import / Export
        cols_export = [c for c in cols_borders if "CH->" in str(c)]
        cols_import = [c for c in cols_borders if "->CH" in str(c)]

        # Sommes horaires (en kWh)
        total_export_kwh = self.df[cols_export].sum(axis=1)
        total_import_kwh = self.df[cols_import].sum(axis=1)

        # --- CALCULS ---
        # 1. Flux Total (Activité du réseau) = Import + Export
        total_flux_kwh = total_import_kwh + total_export_kwh
        
        # 2. Transit Pur (Modèle Ingénieur) = min(Import, Export)
        transit_pure_kwh = np.minimum(total_import_kwh, total_export_kwh)

        # --- DATAFRAME ---
        df_plot = pd.DataFrame(index=self.df.index)
        df_plot['Total_Flux_MW'] = total_flux_kwh.resample('h').sum() / 1000
        df_plot['Transit_Pure_MW'] = transit_pure_kwh.resample('h').sum() / 1000
        
        # Récupération Conso
        col_conso = next((c for c in self.df.columns if "Summe verbrauchte" in str(c)), None)
        if col_conso:
             df_plot['Consumption_MW'] = self.df[col_conso].resample('h').sum() / 1000
        elif 'Consumption_MW' in self.df.columns:
             df_plot['Consumption_MW'] = self.df['Consumption_MW']

        return df_plot

    def plot_total_activity_raw(self):
        """Graphe 1 : L'Activité Brute (La Nervosité)"""
        print("Génération Graphe : Activité Ttansfrontalière Totale (Brut)...")
        df_plot = self._prepare_data()
        if df_plot is None: return

        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(14, 7))

        plt.plot(df_plot.index, df_plot['Consumption_MW'], label="Conso", color='#c0392b', lw=0.5, alpha=0.8)
        plt.plot(df_plot.index, df_plot['Total_Flux_MW'], label="Flux Total (Imp+Exp)", color='#8e44ad', lw=0.5, alpha=0.8)

        plt.title("Le 'Pouls' du Réseau : Volatilité Horaire des Échanges (2025)", fontsize=16, fontweight='bold')
        plt.ylabel("Puissance (MW)")
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.show()

    def plot_total_activity_smoothed(self):
        """Graphe 2 : L'Activité Lissée (Le Volume)"""
        print("Génération Graphe : Activité Transfrontalière Totale (Lissée)...")
        df_plot = self._prepare_data()
        if df_plot is None: return
        
        df_smooth = df_plot.rolling(window=168, center=True).mean().dropna()

        plt.figure(figsize=(14, 7))
        plt.plot(df_smooth.index, df_smooth['Consumption_MW'], label="Conso", color='#c0392b', lw=2)
        plt.plot(df_smooth.index, df_smooth['Total_Flux_MW'], label="Flux Total", color='#8e44ad', lw=2)
        plt.fill_between(df_smooth.index, df_smooth['Total_Flux_MW'], df_smooth['Consumption_MW'],
                         where=(df_smooth['Total_Flux_MW'] > df_smooth['Consumption_MW']), color='#8e44ad', alpha=0.15)
        
        plt.title("La Plaque Tournante : Flux Total vs Consommation (Lissé 7j)", fontsize=16, fontweight='bold')
        plt.ylabel("Puissance (MW)")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_pure_transit(self):
        """Graphe 3 : Le Transit Pur (Ce qui ne fait que traverser)"""
        print("Génération Graphe : Transit Pur (Le Vrai Hub)...")
        df_plot = self._prepare_data()
        if df_plot is None: return
        
        # On lisse aussi celui-là pour bien voir la tendance par rapport à la Conso
        df_smooth = df_plot.rolling(window=168, center=True).mean().dropna()

        plt.figure(figsize=(14, 7))
        plt.plot(df_smooth.index, df_smooth['Consumption_MW'], label="Consommation Suisse", color='#c0392b', lw=2)
        plt.plot(df_smooth.index, df_smooth['Transit_Pure_MW'], label="Transit Pur (Flux Traversant)", color='#2980b9', lw=2)
        plt.fill_between(df_smooth.index, df_smooth['Transit_Pure_MW'], color='#2980b9', alpha=0.2)

        plt.title("Le 'Vrai' Transit : Énergie traversant la Suisse sans être consommée (Lissé 7j)", fontsize=16, fontweight='bold')
        plt.ylabel("Puissance (MW)")
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.show()