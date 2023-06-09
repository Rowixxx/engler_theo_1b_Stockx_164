"""Gestion des "routes" FLASK et des données pour les genres.
Fichier : gestion_genres_crud.py
Auteur : OM 2021.03.16
"""
from pathlib import Path

from flask import redirect
from flask import request
from flask import session
from flask import url_for

from APP_FILMS_164 import app
from APP_FILMS_164.database.database_tools import DBconnection
from APP_FILMS_164.erreurs.exceptions import *
from APP_FILMS_164.clients.gestion_clients_wtf_forms import FormWTFAjouterGenres
from APP_FILMS_164.clients.gestion_clients_wtf_forms import FormWTFDeleteGenre
from APP_FILMS_164.clients.gestion_clients_wtf_forms import FormWTFUpdateGenre

"""
    Auteur : OM 2021.03.16
    Définition d'une "route" /genres_afficher
    
    Test : ex : http://127.0.0.1:5575/genres_afficher
    
    Paramètres : order_by : ASC : Ascendant, DESC : Descendant
                id_genre_sel = 0 >> tous les genres.
                id_genre_sel = "n" affiche le genre dont l'id est "n"
"""


@app.route("/clients_afficher/<string:order_by>/<int:id_genre_sel>", methods=['GET', 'POST'])
def clients_afficher(order_by, id_genre_sel):
    if request.method == "GET":
        try:
            with DBconnection() as mc_afficher:
                if order_by == "ASC" and id_genre_sel == 0:
                    strsql_genres_afficher = """Select id_perso, prenom, nom, date_naissance, sexe, nationalité FROM t_personne ORDER BY id_perso"""
                    mc_afficher.execute(strsql_genres_afficher)
                elif order_by == "ASC":
                    # C'EST LA QUE VOUS ALLEZ DEVOIR PLACER VOTRE PROPRE LOGIQUE MySql
                    # la commande MySql classique est "SELECT * FROM t_genre"
                    # Pour "lever"(raise) une erreur s'il y a des erreurs sur les noms d'attributs dans la table
                    # donc, je précise les champs à afficher
                    # Constitution d'un dictionnaire pour associer l'id du genre sélectionné avec un nom de variable
                    valeur_id_genre_selected_dictionnaire = {"value_id_genre_selected": id_genre_sel}
                    strsql_genres_afficher = """Select id_perso, prenom, nom, date_naissance, sexe, nationalité FROM t_personne ORDER BY id_perso"""

                    mc_afficher.execute(strsql_genres_afficher, valeur_id_genre_selected_dictionnaire)
                else:
                    strsql_genres_afficher = """Select id_perso, prenom, nom, date_naissance, sexe, nationalité FROM t_personne ORDER BY id_perso"""

                    mc_afficher.execute(strsql_genres_afficher)

                data_genres = mc_afficher.fetchall()

                print("data_genres ", data_genres, " Type : ", type(data_genres))

                # Différencier les messages si la table est vide.
                if not data_genres and id_genre_sel == 0:
                    flash("""La table "t_perso" est vide. !!""", "warning")
                elif not data_genres and id_genre_sel > 0:
                    # Si l'utilisateur change l'id_genre dans l'URL et que le genre n'existe pas,
                    flash(f"Le clients demandé n'existe pas !!", "warning")
                else:
                    # Dans tous les autres cas, c'est que la table "t_genre" est vide.
                    # OM 2020.04.09 La ligne ci-dessous permet de donner un sentiment rassurant aux utilisateurs.
                    flash(f"Données clients affichés !!", "success")

        except Exception as Exception_genres_afficher:
            raise ExceptionGenresAfficher(f"fichier : {Path(__file__).name}  ;  "
                                          f"{clients_afficher.__name__} ; "
                                          f"{Exception_genres_afficher}")

    # Envoie la page "HTML" au serveur.
    return render_template("clients/clients_afficher.html", data=data_genres)


"""
    Auteur : OM 2021.03.22
    Définition d'une "route" /genres_ajouter
    
    Test : ex : http://127.0.0.1:5575/genres_ajouter
    
    Paramètres : sans
    
    But : Ajouter un genre pour un film
    
    Remarque :  Dans le champ "name_genre_html" du formulaire "genres/genres_ajouter.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@app.route("/clients_ajouter", methods=['GET', 'POST'])
def clients_ajouter_wtf():
    form = FormWTFAjouterGenres()
    if request.method == "POST":
        try:
            if form.validate_on_submit():
                prenom_client = form.prenom_client.data
                nom_client = form.nom_client.data
                date_naissance_client = form.date_naissance_client.data
                sexe_client = form.sexe_client.data
                nationalite_client = form.nationalite_client.data

                valeurs_insertion_dictionnaire = {"value_prenom_client": prenom_client,
                                                  "value_nom_client": nom_client,
                                                  "value_date_naissance_client": date_naissance_client,
                                                  "value_sexe_client": sexe_client,
                                                  "value_nationalite_client": nationalite_client,
                                                  }
                print("valeurs_insertion_dictionnaire ", valeurs_insertion_dictionnaire)

                strsql_insert_genre = """INSERT INTO t_personne (prenom, nom, date_naissance, sexe, nationalité) 
                VALUES (%(value_prenom_client)s, %(value_nom_client)s, %(value_date_naissance_client)s, 
                %(value_sexe_client)s, %(value_nationalite_client)s)"""

                with DBconnection() as mconn_bd:
                    mconn_bd.execute(strsql_insert_genre, valeurs_insertion_dictionnaire)

                flash(f"Données insérées !!", "success")
                print(f"Données insérées !!")

                # Pour afficher et constater l'insertion de la valeur, on affiche en ordre inverse. (DESC)
                return redirect(url_for('clients_afficher', order_by='DESC', id_genre_sel=0))

        except Exception as Exception_genres_ajouter_wtf:
            raise ExceptionGenresAjouterWtf(f"fichier : {Path(__file__).name}  ;  "
                                            f"{clients_ajouter_wtf.__name__} ; "
                                            f"{Exception_genres_ajouter_wtf}")

    return render_template("clients/clients_ajouter_wtf.html", form=form)


"""
    Auteur : OM 2021.03.29
    Définition d'une "route" /genre_update
    
    Test : ex cliquer sur le menu "genres" puis cliquer sur le bouton "EDIT" d'un "genre"
    
    Paramètres : sans
    
    But : Editer(update) un genre qui a été sélectionné dans le formulaire "genres_afficher.html"
    
    Remarque :  Dans le champ "nom_genre_update_wtf" du formulaire "genres/genre_update_wtf.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@app.route("/clients_update", methods=['GET', 'POST'])
def clients_update_wtf():
    # L'utilisateur vient de cliquer sur le bouton "EDIT". Récupère la valeur de "id_genre"
    id_genre_update = request.values['id_genre_btn_edit_html']

    # Objet formulaire pour l'UPDATE
    form_update = FormWTFUpdateGenre()
    try:
        print(" on submit ", form_update.validate_on_submit())
        if form_update.validate_on_submit():
            prenom_client = form_update.prenom_client.data
            nom_client = form_update.nom_client.data
            date_naissance_client = form_update.date_naissance_client.data
            sexe_client = form_update.sexe_client.data
            nationalite_client = form_update.nationalite_client.data

            valeur_update_dictionnaire = {"value_prenom_client": prenom_client,
                                          "value_nom_client": nom_client,
                                          "value_date_naissance_client": date_naissance_client,
                                          "value_sexe_client": sexe_client,
                                          "value_nationalite_client": nationalite_client,
                                          "value_id_genre": id_genre_update,
                                          }
            print("valeur_update_dictionnaire ", valeur_update_dictionnaire)

            str_sql_update_intitulegenre = """UPDATE t_personne SET prenom = %(value_prenom_client)s,
            nom = %(value_nom_client)s, date_naissance = %(value_date_naissance_client)s, sexe = %(value_sexe_client)s, 
            nationalité = %(value_nationalite_client)s WHERE id_perso = %(value_id_genre)s"""
            with DBconnection() as mconn_bd:
                mconn_bd.execute(str_sql_update_intitulegenre, valeur_update_dictionnaire)

            flash(f"Donnée mise à jour !!", "success")
            print(f"Donnée mise à jour !!")

            # afficher et constater que la donnée est mise à jour.
            # Affiche seulement la valeur modifiée, "ASC" et l'"id_genre_update"
            return redirect(url_for('clients_afficher', order_by="ASC", id_genre_sel=id_genre_update))
        elif request.method == "GET":
            # Opération sur la BD pour récupérer "id_genre" et "intitule_genre" de la "t_genre"
            str_sql_id_genre = "SELECT id_perso, prenom, nom, date_naissance, sexe, nationalité FROM t_personne " \
                               "WHERE id_perso = %(value_id_genre)s"
            valeur_select_dictionnaire = {"value_id_genre": id_genre_update}
            with DBconnection() as mybd_conn:
                mybd_conn.execute(str_sql_id_genre, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()", vu qu'il n'y a qu'un seul champ "nom genre" pour l'UPDATE
            data_nom_genre = mybd_conn.fetchone()
            #print("data_nom_genre ", data_nom_genre, " type ", type(data_nom_genre), " genre ",
             #     data_nom_genre["intitule_genre"])

            # Afficher la valeur sélectionnée dans les champs du formulaire "genre_update_wtf.html"
            form_update.prenom_client.data = data_nom_genre["prenom"]
            form_update.nom_client.data = data_nom_genre["nom"]
            form_update.date_naissance_client.data = data_nom_genre["date_naissance"]
            form_update.sexe_client.data = data_nom_genre["sexe"]
            form_update.nationalite_client.data = data_nom_genre["nationalité"]


    except Exception as Exception_genre_update_wtf:
        raise ExceptionGenreUpdateWtf(f"fichier : {Path(__file__).name}  ;  "
                                      f"{clients_update_wtf.__name__} ; "
                                      f"{Exception_genre_update_wtf}")

    return render_template("clients/clients_update_wtf.html", form_update=form_update)


"""
    Auteur : OM 2021.04.08
    Définition d'une "route" /genre_delete
    
    Test : ex. cliquer sur le menu "genres" puis cliquer sur le bouton "DELETE" d'un "genre"
    
    Paramètres : sans
    
    But : Effacer(delete) un genre qui a été sélectionné dans le formulaire "genres_afficher.html"
    
    Remarque :  Dans le champ "nom_genre_delete_wtf" du formulaire "genres/genre_delete_wtf.html",
                le contrôle de la saisie est désactivée. On doit simplement cliquer sur "DELETE"
"""


@app.route("/clients_delete", methods=['GET', 'POST'])
def clients_delete_wtf():
    data_films_attribue_genre_delete = None
    data_nom_genre = None
    btn_submit_del = None
    # L'utilisateur vient de cliquer sur le bouton "DELETE". Récupère la valeur de "id_genre"
    id_genre_delete = request.values['id_genre_btn_delete_html']

    # Objet formulaire pour effacer le genre sélectionné.
    form_delete = FormWTFDeleteGenre()
    try:
        print(" on submit ", form_delete.validate_on_submit())
        if request.method == "POST" and form_delete.validate_on_submit():

            if form_delete.submit_btn_annuler.data:
                return redirect(url_for("clients_afficher", order_by="ASC", id_genre_sel=0))

            if form_delete.submit_btn_conf_del.data:
                # Récupère les données afin d'afficher à nouveau
                # le formulaire "genres/genre_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                #data_films_attribue_genre_delete = session['data_films_attribue_genre_delete']
                #print("data_films_attribue_genre_delete ", data_films_attribue_genre_delete)
                data_nom_genre = session['data_personne']
                form_delete.client_delete_wtf.data = data_nom_genre['prenom']

                flash(f"Effacer le genre de façon définitive de la BD !!!", "danger")
                # L'utilisateur vient de cliquer sur le bouton de confirmation pour effacer...
                # On affiche le bouton "Effacer genre" qui va irrémédiablement EFFACER le genre
                btn_submit_del = True

            if form_delete.submit_btn_del.data:
                valeur_delete_dictionnaire = {"value_id_genre": id_genre_delete}
                print("valeur_delete_dictionnaire ", valeur_delete_dictionnaire)

                str_sql_delete_films_genre = """DELETE FROM t_personne WHERE id_perso = %(value_id_genre)s"""
                #str_sql_delete_idgenre = """DELETE FROM t_genre WHERE id_genre = %(value_id_genre)s"""
                # Manière brutale d'effacer d'abord la "fk_genre", même si elle n'existe pas dans la "t_genre_film"
                # Ensuite on peut effacer le genre vu qu'il n'est plus "lié" (INNODB) dans la "t_genre_film"
                with DBconnection() as mconn_bd:
                    mconn_bd.execute(str_sql_delete_films_genre, valeur_delete_dictionnaire)
                    #mconn_bd.execute(str_sql_delete_idgenre, valeur_delete_dictionnaire)

                flash(f"Chaussure définitivement effacée !!", "success")
                print(f"Chaussure définitivement effacée !!")

                # afficher les données
                return redirect(url_for('clients_afficher', order_by="ASC", id_genre_sel=0))

        if request.method == "GET":
            valeur_select_dictionnaire = {"value_id_genre": id_genre_delete}
            print(id_genre_delete, type(id_genre_delete))

            # Requête qui affiche tous les films_genres qui ont le genre que l'utilisateur veut effacer
            #str_sql_genres_films_delete = """SELECT id_genre_film, nom_film, id_genre, intitule_genre FROM t_genre_film
             #                               INNER JOIN t_film ON t_genre_film.fk_film = t_film.id_film
              #                              INNER JOIN t_genre ON t_genre_film.fk_genre = t_genre.id_genre
               #                             WHERE fk_genre = %(value_id_genre)s"""

            with DBconnection() as mydb_conn:
                #mydb_conn.execute(str_sql_genres_films_delete, valeur_select_dictionnaire)
                #data_films_attribue_genre_delete = mydb_conn.fetchall()
                #print("data_films_attribue_genre_delete...", data_films_attribue_genre_delete)

                # Nécessaire pour mémoriser les données afin d'afficher à nouveau
                # le formulaire "genres/genre_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                #session['data_films_attribue_genre_delete'] = data_films_attribue_genre_delete

                # Opération sur la BD pour récupérer "id_genre" et "intitule_genre" de la "t_genre"
                str_sql_id_genre = "SELECT id_perso, prenom FROM t_personne WHERE id_perso = %(value_id_genre)s"

                mydb_conn.execute(str_sql_id_genre, valeur_select_dictionnaire)
                # Une seule valeur est suffisante "fetchone()",
                # vu qu'il n'y a qu'un seul champ "nom genre" pour l'action DELETE
                data_nom_genre = mydb_conn.fetchone()
                session['data_personne'] = data_nom_genre
                #print("data_nom_genre ", data_nom_genre, " type ", type(data_nom_genre), " genre ",
                 #     data_nom_genre["intitule_genre"]) c'est à cause de ce print mince'

            # Afficher la valeur sélectionnée dans le champ du formulaire "genre_delete_wtf.html"
            form_delete.client_delete_wtf.data = data_nom_genre["prenom"]

            # Le bouton pour l'action "DELETE" dans le form. "genre_delete_wtf.html" est caché.
            btn_submit_del = False

    except Exception as Exception_genre_delete_wtf:
        raise ExceptionGenreDeleteWtf(f"fichier : {Path(__file__).name}  ;  "
                                      f"{clients_delete_wtf.__name__} ; "
                                      f"{Exception_genre_delete_wtf}")

    return render_template("clients/clients_delete_wtf.html",
                           form_delete=form_delete,
                           btn_submit_del=btn_submit_del,
                           data_nom_genre=data_nom_genre)
