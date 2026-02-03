from flask import Flask, render_template, request, redirect, flash, url_for
from flask_mysqldb import MySQL
import ping3
from datetime import datetime
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Clé secrète obligatoire pour les flash messages et sessions
app.secret_key = 'netwatch_secret_key_daouda_2026_senegal_change_this_please'

# Chargement de la configuration (config.py)
app.config.from_pyfile('config.py')

# Configuration email (à mettre dans config.py ou .env)
app.config['MAIL_SERVER'] = 'smtp.mail.me.com'         # serveur iCloud
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'daoudambow2000@icloud.com'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # mot de passe d'application iCloud

mysql = MySQL(app)
mail = Mail(app)

# Injecte l'année actuelle dans tous les templates
@app.context_processor
def inject_current_year():
    return dict(current_year=datetime.now().year)


# Page d'accueil / Dashboard
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    cur = mysql.connection.cursor()
    
    # Gestion de l'ajout d'équipement
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        ip = request.form.get('ip', '').strip()
        type_eq = request.form.get('type', '').strip()
        
        if nom and ip:
            try:
                cur.execute(
                    "INSERT INTO equipements (nom, ip, type) VALUES (%s, %s, %s)",
                    (nom, ip, type_eq or 'Inconnu')
                )
                mysql.connection.commit()
                flash("Équipement ajouté avec succès !", "success")
            except Exception as e:
                mysql.connection.rollback()
                flash(f"Erreur lors de l'ajout : {str(e)}", "error")
                print("Erreur insertion :", e)
        else:
            flash("Nom et IP sont obligatoires", "error")
        
        return redirect(url_for('dashboard'))

    # Récupération des équipements + calcul du statut
    cur.execute("SELECT * FROM equipements")
    columns = [desc[0] for desc in cur.description]  # ['id', 'nom', 'ip', 'type']
    rows = cur.fetchall()
    
    equipements = []
    for row in rows:
        eq = dict(zip(columns, row))
        delay = ping3.ping(eq['ip'], timeout=1.5)
        eq['status'] = 'En ligne' if delay is not None else 'Hors ligne'
        eq['status_class'] = 'status-online' if delay is not None else 'status-offline'
        eq['latency'] = round(delay * 1000, 1) if delay else None
        equipements.append(eq)
    
    cur.close()
    
    return render_template('dashboard.html', equipements=equipements, active_tab='dashboard')


# Route pour tester un ping spécifique
@app.route('/ping/<ip>')
def ping(ip):
    try:
        delay = ping3.ping(ip, timeout=2)
        if delay is not None:
            flash(f"{ip} : UP ({round(delay * 1000, 2)} ms)", "success")
        else:
            flash(f"{ip} : DOWN (pas de réponse)", "error")
    except Exception as e:
        flash(f"{ip} : Erreur ({str(e)})", "error")
    
    return redirect(url_for('dashboard'))


# Route pour la page Scan Local
@app.route('/scan')
def scan():
    return render_template('scan.html', active_tab='scan')


# Route pour la page Contacts
@app.route('/contacts')
def contacts():
    return render_template('contacts.html', active_tab='contacts')


# Route pour traiter le formulaire de contact (POST)
@app.route('/contact', methods=['POST'])
def contact_submit():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    message = request.form.get('message', '').strip()
    
    if not all([name, email, message]):
        flash("Nom, email et message sont obligatoires", "error")
        return redirect(url_for('contacts'))
    
    # Envoi d'email à toi (l'admin)
    msg = Message(
        subject=f"Nouveau message de contact - {name}",
        sender=email,
        recipients=['daoudambow2000@icloud.com']  # ton email
    )
    msg.body = f"""
    Nouveau message reçu via le site NetWatch :

    Nom       : {name}
    Email     : {email}
    Téléphone : {phone or 'Non indiqué'}
    Message   :
    {message}
    """
    
    try:
        mail.send(msg)
        flash("Message envoyé avec succès ! Nous vous répondrons rapidement.", "success")
    except Exception as e:
        flash(f"Erreur lors de l'envoi du message : {str(e)}", "error")
        print("Erreur envoi email :", str(e))
    
    return redirect(url_for('contacts'))


# Route pour la page Statistiques
@app.route('/stats')
def stats():
    return render_template('stats.html', active_tab='stats')


# Route pour la page Paramètres
@app.route('/settings')
def settings():
    return render_template('settings.html', active_tab='settings')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
