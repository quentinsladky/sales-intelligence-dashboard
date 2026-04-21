import sqlite3
import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd


conn = sqlite3.connect("/Users/quentin/Desktop/sales_intelligence") #setup connexion
cursor = conn.cursor() #setup stylo 


# Configuration
# Création table ventes
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produit_id INTEGER,
        quantite INTEGER,
        date_vente TEXT,
        chiffre_affaires REAL
    )
""")

# Création données aleatoires T-shirt 
mois = np.arange(1, 13)  # 12 mois
saisonnalite_tshirts = np.array([1.0, 1.1, 1.2, 1.3, 1.5, 1.7, 1.7, 1.4, 1.2, 1.1, 0.8, 0.7]) #plus de ventes en été et moins en hiver
ventes_tshirts = np.round((30 + mois * 1.5) * saisonnalite_tshirts + np.random.normal(0, 3, 12))# Ventes avec tendance + bruit aléatoire
# Création données aleatoires Jeans 
saisonnalite_jeans = np.array([1.2, 1.1, 1, 1, 1, 0.9, 0.9, 1.1, 1.2, 1.1, 1.2, 1.3]) #ventes plutot linéaires sur l'année
ventes_jeans = np.round((30 + mois * 1.5) * saisonnalite_jeans + np.random.normal(0, 3, 12))
# Création données aleatoires Vestes
saisonnalite_vestes = np.array([1.3, 1.2, 1.0, 0.8, 0.7, 0.6, 0.7, 0.8, 1.0, 1.1, 1.3, 1.4]) #plus de ventes en hiver et moins en été 
ventes_vestes = np.round((30 + mois * 1.5) * saisonnalite_vestes + np.random.normal(0, 3, 12))
print(ventes_tshirts)
print(ventes_jeans)
print(ventes_vestes)

# Création des dates mensuelles 
date = []
for k in range (1,13): 
    date.append(f"2025-{k:02d}-01")
print(date)

# Vérifie si les ventes existent déjà
cursor.execute("SELECT COUNT(*) FROM ventes")
ventes_count = cursor.fetchone()[0]

# Prix produits
prix = {1: 35, 2: 85, 3: 90}  #Cf structure des autres projets 

if ventes_count == 0:
    for i in range(12):        
       
        # T-shirt (produit_id = 1)
        cursor.execute("""
            INSERT INTO ventes (produit_id, quantite, date_vente, chiffre_affaires)
            VALUES (?, ?, ?, ?)
        """, (1, int(ventes_tshirts[i]), date[i], int(ventes_tshirts[i]) * prix[1]))
        
         # Jeans (produit_id = 2)
        cursor.execute("""
            INSERT INTO ventes (produit_id, quantite, date_vente, chiffre_affaires)
            VALUES (?, ?, ?, ?)
        """, (2, int(ventes_jeans[i]), date[i], int(ventes_jeans[i]) * prix[2]))
        
         # Vestes (produit_id = 3)
        cursor.execute("""
            INSERT INTO ventes (produit_id, quantite, date_vente, chiffre_affaires)
            VALUES (?, ?, ?, ?)
        """, (3, int(ventes_vestes[i]), date[i], int(ventes_vestes[i]) * prix[3]))
        
# Tableau affiché avec pandas
df = pd.read_sql("SELECT * FROM ventes", conn)
print(df)


# 1 : Quel produit génère le plus de CA et est-ce cohérent avec son volume de ventes ?
df_grouped = df.groupby("produit_id")[["chiffre_affaires", "quantite"]].sum()
# Figure 
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.bar(df_grouped.index, df_grouped["chiffre_affaires"], color='b', label='CA en €')
ax1.set_xticks([1, 2, 3])
ax1.set_xticklabels(["T-shirt", "Jean", "Veste"])
ax1.set_ylabel("Chiffre d'affaires (€)", color='b')
ax2 = ax1.twinx()
ax2.bar(df_grouped.index + 0.3, df_grouped["quantite"], width=0.3, color='r', label='Quantité')
ax2.set_ylabel("Quantité vendue", color='r')
plt.title("CA vs Volume par produit")
plt.savefig("/Users/quentin/Desktop/graph_mixte.png", dpi=150)
plt.show()
plt.close()
print(df_grouped)


# 2 : Quel est le meilleur mois pour chaque produit ? Y a-t-il des mois à risque ?
df_tshirt = df[df["produit_id"] == 1]
df_jeans = df[df["produit_id"] == 2]
df_vestes = df[df["produit_id"] == 3]
print(df_tshirt)
print(df_jeans)
print(df_vestes)
# Figure
plt.figure(figsize=(15, 6))
plt.plot(df_tshirt["date_vente"], df_tshirt["chiffre_affaires"], label="T-shirt", color="b")
plt.plot(df_jeans["date_vente"], df_jeans["chiffre_affaires"], label="Jean", color="r")
plt.plot(df_vestes["date_vente"], df_vestes["chiffre_affaires"], label="Veste", color="g")
plt.title("Saisonnalité des ventes par produit")
plt.legend()
plt.savefig("/Users/quentin/Desktop/graph_saisonnalite.png", dpi=150)
plt.close()


# 3 : Les ventes sont-elles en croissance sur l'année ? À quel rythme ?
# Calcul du CA mensuel total 
CA_mensuel = df.groupby("date_vente")["chiffre_affaires"].sum()
print(CA_mensuel)
MOIS = np.arange(1,13)
CA_mensuel_valeurs = CA_mensuel.values
COEFFS = np.polyfit(MOIS, CA_mensuel_valeurs, 1)
TENDANCE = np.poly1d(COEFFS)
print(f"CA prévu mois 1 : {TENDANCE(1):.0f} €")
print(f"CA prévu mois 12 : {TENDANCE(12):.0f} €")
print(f"Croissance mensuelle : {COEFFS[0]:.0f} €/mois")
# Figure
plt.figure(figsize=(12, 6))
plt.plot(MOIS, CA_mensuel_valeurs, label="CA réel mensuel", color="b")
plt.plot(MOIS, TENDANCE(MOIS), label="Tendance", color="r",)
plt.title("CA réel et tendance")
plt.legend()
plt.savefig("/Users/quentin/Desktop/graph_tendance_CA.png", dpi=150)
plt.close()


# 4 : Quelle est la part de chaque produit dans le CA total ?
# Calcul des pourcentages en Pandas
df_grouped["part_CA"] = df_grouped["chiffre_affaires"] / df_grouped["chiffre_affaires"].sum() * 100
print(df_grouped["part_CA"].round(1))
# Figure
plt.pie(
    df_grouped["part_CA"],
    labels=["T-shirt", "Jean", "Veste"],
    autopct="%1.1f%%",  # affiche les % sur chaque part
    colors=["b", "r", "g"]
)
plt.legend()
plt.savefig("/Users/quentin/Desktop/graph_part_produit_CA.png", dpi=150)
plt.close()


# 5 : Quel CA peut-on anticiper pour les 3 prochains mois ?
print(f"CA prévu mois 13 : {TENDANCE(13):.0f} €")
print(f"CA prévu mois 14 : {TENDANCE(14):.0f} €")
print(f"CA prévu mois 15 : {TENDANCE(15):.0f} €")
VENTES = np.array([20,25,23,32,44,39,43,50,53,54,61,55])
MOIS_FUTURS = np.array([12,13,14,15]) 
MOIS_PREVISIONS = np.array([CA_mensuel_valeurs[-1], TENDANCE(13), TENDANCE(14), TENDANCE(15)])
# Figure 
plt.figure(figsize=(12, 6))
plt.plot(MOIS, CA_mensuel_valeurs,label="CA réel", color="b") 
plt.plot(MOIS_FUTURS, MOIS_PREVISIONS, "r--", label="Ventes futures")
plt.title("CA réel et prévisions 3 mois")
plt.xlabel("Mois") 
plt.ylabel("CA (€)") 
plt.savefig("/Users/quentin/Desktop/graph_anticipation_CA_3m.png", dpi=150)
plt.show()

conn.close()
