import matplotlib.pyplot as plt
import seaborn as sns

class SwissGridVisualizer:
    def __init__(self, df):
        self.df = df

    def plot_winter_gap(self):
        # Configuration du style graphique
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(12, 6))

        # Tracer les courbes (Conso vs Prod)
        plt.plot(self.df.index, self.df['Consumption_MW'], label='Consommation (Demande)', color='#E74C3C', lw=1)
        plt.plot(self.df.index, self.df['Production_MW'], label='Production (Offre)', color='#2ECC71', lw=1)

        # Zone ROUGE : Le Winter Gap (On doit importer)
        plt.fill_between(self.df.index, 
                         self.df['Consumption_MW'], 
                         self.df['Production_MW'], 
                         where=(self.df['Consumption_MW'] > self.df['Production_MW']),
                         color='#E74C3C', alpha=0.3, label='Winter Gap (Imports requis)')

        # Zone VERTE : Le Surplus Estival (On exporte)
        plt.fill_between(self.df.index, 
                         self.df['Consumption_MW'], 
                         self.df['Production_MW'], 
                         where=(self.df['Production_MW'] > self.df['Consumption_MW']),
                         color='#2ECC71', alpha=0.3, label='Surplus (Exports possibles)')

        # Titres et légendes
        plt.title("Simulation du 'Winter Gap' Suisse : Le Défi Structurel", fontsize=14, fontweight='bold')
        plt.ylabel("Puissance (MW)")
        plt.xlabel("Mois")
        plt.legend(loc='upper right')
        plt.tight_layout()
        
        print("Graphique généré. Ferme la fenêtre pour terminer le script.")
        plt.show()