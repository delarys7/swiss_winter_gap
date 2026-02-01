import pandas as pd
import numpy as np

class SwissGridGenerator:
    def __init__(self, year=2025):
        self.year = year

    def generate_year_data(self):
        """
        Simule le profil énergétique suisse (8760 heures).
        Hiver : Conso > Prod (Déficit). Été : Prod > Conso (Surplus).
        """
        # Création de l'axe temporel (heures)
        dates = pd.date_range(start=f'{self.year}-01-01', end=f'{self.year}-12-31 23:00', freq='h')
        hours = np.arange(len(dates))
        
        # Consommation : Pic en hiver (Chauffage), Creux en été
        conso_base = 6000
        conso_seasonality = 1500 * np.cos((hours) * 2 * np.pi / 8760) 
        noise_conso = np.random.normal(0, 200, len(dates))
        consumption = conso_base + conso_seasonality + noise_conso

        # Production (Hydro) : Pic en été (Fonte des neiges), Creux en hiver
        prod_base = 5800
        prod_seasonality = -2000 * np.cos((hours) * 2 * np.pi / 8760)
        noise_prod = np.random.normal(0, 300, len(dates))
        production = prod_base + prod_seasonality + noise_prod

        # Assemblage dans un DataFrame
        df = pd.DataFrame(index=dates)
        df['Consumption_MW'] = consumption
        df['Production_MW'] = production
        
        return df