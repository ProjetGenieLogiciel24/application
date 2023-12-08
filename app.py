# Importer les modules nécessaires
import sqlite3
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

# Créer la base de données SQLite
conn = sqlite3.connect("devis.db")
c = conn.cursor()

# Créer la table pour stocker les coûts de construction
c.execute("""CREATE TABLE IF NOT EXISTS couts (
    categorie TEXT,
    description TEXT,
    prix REAL
)""")

# Insérer des données de test dans la table
c.execute("""INSERT INTO couts VALUES (
    "Terrassement",
    "Fouilles en pleine masse",
    1500.00
)""")

c.execute("""INSERT INTO couts VALUES (
    "Fondations",
    "Semelles filantes",
    2500.00
)""")

# Valider les changements dans la base de données
conn.commit()

# Fermer la connexion à la base de données
conn.close()

# Définir la classe de l'écran d'accueil
class AccueilScreen(Screen):
    # Définir la fonction qui sera appelée lorsque le bouton "Commencer le devis" sera pressé
    def on_press_accueil(self):
        # Changer l'écran courant pour l'écran de devis
        self.manager.current = "devis"

# Définir la classe de l'écran de devis
class DevisScreen(Screen):
    # Définir la fonction qui sera appelée lorsque le bouton "Valider le devis" sera pressé
    def on_press_devis(self):
        # Récupérer les valeurs saisies par l'utilisateur
        nom = self.ids.nom.text
        adresse = self.ids.adresse.text
        type = self.ids.type.text
        surface = self.ids.surface.text
        # Vérifier que les valeurs sont valides
        if nom and adresse and type and surface:
            try:
                # Convertir la surface en nombre réel
                surface = float(surface)
                # Calculer le coût total de la construction
                cout_total = self.calculer_cout(type, surface)
                # Formater le résultat du devis
                resultat = f"Nom du client : {nom}\n"
                resultat += f"Adresse du client : {adresse}\n"
                resultat += f"Type de maison : {type}\n"
                resultat += f"Surface de la maison : {surface} m2\n"
                resultat += f"Coût total : {cout_total} FCFA\n"
                # Afficher le résultat sur l'écran de résultat
                self.manager.get_screen("resultat").ids.resultat.text = resultat
                # Changer l'écran courant pour l'écran de résultat
                self.manager.current = "resultat"
            except ValueError:
                # Afficher un message d'erreur si la surface n'est pas un nombre valide
                self.manager.get_screen("devis").ids.devis.text = "Veuillez renseigner les informations suivantes pour générer votre devis\n\t      La surface doit être un nombre réel."
                self.manager.current = "devis"
        else:
            # Afficher un message d'erreur si les champs sont vides
            self.manager.get_screen("devis").ids.devis.text = "Veuillez renseigner les informations suivantes pour générer votre devis\n\t      Veuillez remplir tous les champs."
            self.manager.current = "devis"

    # Définir la fonction qui calcule le coût total de la construction en fonction du type et de la surface de la maison
    def calculer_cout(self, type, surface):
        # Ouvrir la connexion à la base de données
        conn = sqlite3.connect("devis.db")
        c = conn.cursor()
        # Initialiser le coût total à zéro
        cout_total = 0
        # Parcourir les lignes de la table des coûts
        for row in c.execute("SELECT * FROM couts"):
            # Récupérer la catégorie, la description et le prix de la ligne
            categorie, description, prix = row
            # Ajouter le prix au coût total
            cout_total += prix
            # Si le type de maison est à étage, ajouter un supplément de 10% pour les fondations et le gros oeuvre
            if type == "A étage" and categorie in ("Fondations", "Gros oeuvre"):
                cout_total += prix * 0.1
            # Si le type de maison est sous-sol, ajouter un supplément de 20% pour le terrassement et les fondations
            if type == "Sous-sol" and categorie in ("Terrassement", "Fondations"):
                cout_total += prix * 0.2
        # Fermer la connexion à la base de données
        conn.close()
        # Multiplier le coût total par la surface de la maison
        cout_total *= surface
        # Arrondir le coût total à deux décimales
        cout_total = round(cout_total, 2)
        # Retourner le coût total
        return cout_total

# Définir la classe de l'écran de résultat
class ResultatScreen(Screen):
    # Définir la fonction qui sera appelée lorsque le bouton "Retour à l'accueil" sera pressé
    def on_press_resultat(self):
        # Changer l'écran courant pour l'écran d'accueil
        self.manager.current = "accueil"

# Définir la classe de l'application
class DevisApp(App):
    # Définir la fonction qui construit l'interface de l'application
    def build(self):
        # Charger le fichier Kv
        Builder.load_file("app.kv")
        # Créer le gestionnaire d'écrans
        sm = ScreenManager()
        # Ajouter les écrans à l'application
        sm.add_widget(AccueilScreen())
        sm.add_widget(DevisScreen())
        sm.add_widget(ResultatScreen())
        # Retourner le gestionnaire d'écrans
        return sm

# Lancer l'application
if __name__ == "__main__":
    DevisApp().run()
