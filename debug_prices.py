import pandas as pd
import matplotlib.pyplot as plt
import os

# CONFIGURATION
# Mets ici le nom EXACT de ton fichier CSV de prix
filename = 'data/SpotPrices_OpenData.xlsx' 
# NOTE: D'après ton upload, il s'appelle .xlsx mais c'est un CSV ? 
# Si c'est un vrai fichier Excel, pd.read_csv ne marchera pas.

print(f"--- DIAGNOSTIC PRIX ---")
print(f"Fichier cible : {filename}")

if not os.path.exists(filename):
    print("❌ ERREUR : Le fichier n'existe pas dans le dossier data/ !")
    exit()

try:
    # 1. Tentative de lecture "Intelligente"
    # On teste si c'est un vrai Excel ou un faux Excel (CSV renommé)
    try:
        df = pd.read_excel(filename)
        print("✅ Format détecté : EXCEL (.xlsx)")
    except:
        print("⚠️ Ce n'est pas un vrai Excel. Tentative lecture CSV...")
        df = pd.read_csv(filename, sep=None, engine='python')
        print("✅ Format détecté : CSV (renommé en .xlsx ?)")

    print(f"Colonnes trouvées : {df.columns.tolist()}")
    print("Aperçu des 5 premières lignes :")
    print(df.head())

    # 2. Nettoyage
    # Si tout est dans une seule colonne
    if len(df.columns) == 1:
        print("\n[INFO] Colonne unique détectée, découpage...")
        # On suppose que c'est du CSV mal lu
        col_name = df.columns[0]
        # On vire les guillemets du nom de la colonne
        clean_col = col_name.replace('"', '').replace("'", "")
        
        # On découpe les données
        df = df.iloc[:, 0].astype(str).str.replace('"', '').str.split(',', expand=True)
        df.columns = ['Datum', 'Price']
    
    # Si on a déjà les colonnes mais avec des noms sales
    df.columns = [c.strip().replace('"', '') for c in df.columns]
    
    # On cherche la colonne Prix
    col_price = next((c for c in df.columns if 'Baseload' in c or 'Price' in c or 'EUR' in c), None)
    col_date = next((c for c in df.columns if 'Datum' in c or 'Date' in c), None)

    if not col_price or not col_date:
        print(f"❌ Impossible d'identifier les colonnes Date/Prix. Colonnes actuelles : {df.columns}")
        exit()

    print(f"\n[INFO] Colonne Prix identifiée : '{col_price}'")
    print(f"[INFO] Colonne Date identifiée : '{col_date}'")

    # 3. Conversion
    df['Date'] = pd.to_datetime(df[col_date], errors='coerce')
    df['Price'] = pd.to_numeric(df[col_price], errors='coerce')

    # 4. Filtre 2025
    df_2025 = df[df['Date'].dt.year == 2025].copy()
    print(f"\n[RESULTAT] Lignes trouvées pour 2025 : {len(df_2025)}")

    if len(df_2025) == 0:
        print("❌ Aucune donnée pour 2025 !")
        print(f"   Plage de dates dispo : {df['Date'].min()} à {df['Date'].max()}")
    else:
        # 5. Plot
        plt.figure(figsize=(12, 6))
        plt.plot(df_2025['Date'], df_2025['Price'], label='Spot Price 2025')
        plt.title(f"Prix Spot Suisse 2025 (Moyenne: {df_2025['Price'].mean():.2f} €)")
        plt.ylabel('EUR/MWh')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
        print("✅ Graphique généré !")

except Exception as e:
    print(f"\n❌ CRASH : {e}")
    import traceback
    traceback.print_exc()