from src.loader import SwissGridLoader
from src.analyzer import WinterGapAnalyzer
from src.visualizer import SwissGridVisualizer
from src.border_analyzer import BorderAnalyzer
from src.transit_analyzer import TransitAnalyzer
from src.cost_analyzer import CostAnalyzer
from src.advanced_stats import AdvancedAnalyzer
import os

def main():
    print("Démarrage Swiss Winter Gap & Border Analysis...")
    
    file_swissgrid = 'swissgrid_2025.xlsx'
    file_prices = 'SpotPrices_OpenData.xlsx'
    filepath_swissgrid = os.path.join('data', file_swissgrid)
    filepath_prices = os.path.join('data', file_prices)
    
    loader = SwissGridLoader(filepath_swissgrid, filepath_prices)
    df = loader.load_data()
    
    if df is not None:
        # 1. Analyse Winter Gap
        analyzer = WinterGapAnalyzer(df)
        df_analyzed = analyzer.analyze()
        visualizer = SwissGridVisualizer(df_analyzed)
        # --- A. Vue Brute (Technique) : Affiche le bruit, les pics horaires, la réalité physique 15min/1h ---
        visualizer.plot_raw_data()
        # --- B. Vue Lissée (Stratégique) : Affiche la tendance globale ---
        visualizer.plot_smoothed_trend()
        
        # 2. Analyse des Frontières
        border = BorderAnalyzer(df)
        border.plot_cross_border_flows()

        # 3. Analyse du Transit
        transit = TransitAnalyzer(df)
        # --- A. Vue Brute (Technique) : Affiche le bruit, les pics horaires, la réalité physique 15min/1h ---
        transit.plot_total_activity_raw()
        # --- B. Vue Lissée (Stratégique) : Affiche la tendance globale ---
        transit.plot_total_activity_smoothed()
        # --- C. Transit pur (Le Vrai Hub) ---
        transit.plot_pure_transit()

        # 4. Analyse Financière
        cost = CostAnalyzer(df)
        cost.plot_financial_balance()

        # 5. ANALYSES AVANCÉES (NOUVEAU)
        print("\n--- Démarrage des Analyses Statistiques Avancées ---")
        adv = AdvancedAnalyzer(df)
        # --- A. La Monotone (Indispensable pour le Winter Gap) ---
        adv.plot_duration_curve()
        # --- B. Le Heatmap (Visuellement top pour le rapport) ---
        adv.plot_seasonal_heatmap()
        # --- C. Corrélation Prix (Pour la partie éco) ---
        adv.plot_price_correlation()
        
    else:
        print("Problème de chargement.")

if __name__ == "__main__":
    main()