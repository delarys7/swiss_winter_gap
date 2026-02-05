import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class TransitAnalyzer:
    def __init__(self, df):
        self.df = df

    def plot_total_activity_raw(self):
        """Graphe 1 : Flux Total vs Conso (Brut)"""
        print("Génération Graphe : Flux Total (Brut)...")
        
        # On vérifie que les colonnes existent (créées par le loader)
        required = ['Consumption_MW', 'Total_Flux_MW']
        if not all(col in self.df.columns for col in required):
            print(f"⚠️ Manque des colonnes MW calculées : {required}")
            return

        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(14, 7))

        plt.plot(self.df.index, self.df['Consumption_MW'], label="Consommation", color='#c0392b', lw=0.5, alpha=0.8)
        plt.plot(self.df.index, self.df['Total_Flux_MW'], label="Flux Total (Imp+Exp)", color='#8e44ad', lw=0.5, alpha=0.8)

        plt.title("Activité Réseau : Flux Total vs Consommation (Brut 2025)", fontsize=16, fontweight='bold')
        plt.ylabel("Puissance Moyenne (MW)")
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.show()

    def plot_total_activity_smoothed(self):
        """Graphe 2 : Flux Total vs Conso (Lissé 7j)"""
        print("Génération Graphe : Flux Total (Lissé)...")
        
        # Lissage direct sur les colonnes MW déjà prêtes
        df_smooth = self.df[['Consumption_MW', 'Total_Flux_MW']].rolling(window=168, center=True).mean().dropna()

        plt.figure(figsize=(14, 7))
        plt.plot(df_smooth.index, df_smooth['Consumption_MW'], label="Consommation", color='#c0392b', lw=2)
        plt.plot(df_smooth.index, df_smooth['Total_Flux_MW'], label="Flux Total", color='#8e44ad', lw=2)
        
        plt.fill_between(df_smooth.index, df_smooth['Total_Flux_MW'], df_smooth['Consumption_MW'],
                         where=(df_smooth['Total_Flux_MW'] > df_smooth['Consumption_MW']), color='#8e44ad', alpha=0.15)
        
        plt.title("La Plaque Tournante : Flux Total vs Consommation (Lissé 7j)", fontsize=16, fontweight='bold')
        plt.ylabel("Puissance (MW)")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_pure_transit(self):
        """Graphe 3 : Transit Pur vs Conso (Lissé 7j)"""
        print("Génération Graphe : Transit Pur...")
        
        if 'Transit_MW' not in self.df.columns:
            print("⚠️ Pas de colonne Transit_MW.")
            return

        df_smooth = self.df[['Consumption_MW', 'Transit_MW']].rolling(window=168, center=True).mean().dropna()

        plt.figure(figsize=(14, 7))
        plt.plot(df_smooth.index, df_smooth['Consumption_MW'], label="Consommation", color='#c0392b', lw=2)
        plt.plot(df_smooth.index, df_smooth['Transit_MW'], label="Transit Pur (Officiel)", color='#2980b9', lw=2)
        
        plt.fill_between(df_smooth.index, df_smooth['Transit_MW'], color='#2980b9', alpha=0.2)

        plt.title("Le Transit Pur vs Consommation (Lissé 7j)", fontsize=16, fontweight='bold')
        plt.ylabel("Puissance (MW)")
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.show()