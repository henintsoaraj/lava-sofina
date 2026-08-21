FROM ubuntu:24.04

# 1. Installer icecast2 via apt
#    Piège à anticiper : l'installation Debian d'icecast2 est "interactive"
#    par défaut (elle pose des questions, comme le mot de passe admin).
#    Dans un Dockerfile, il n'y a personne pour répondre à ces questions.
#    → Cherche "apt install debconf noninteractive icecast2" pour voir
#      comment forcer une installation silencieuse.

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    libxml2 \
    icecast2 \
    && rm -rf /var/lib/apt/lists/*


# 2. Copier TON fichier icecast.xml (celui que tu as déjà, sans le
#    changeowner) à l'endroit où Icecast l'attend dans l'image
COPY icecast.xml /etc/icecast2/

RUN mkdir -p /usr/local/var/log/icecast /usr/local/share/icecast/web && chown -R icecast2:icecast /usr/local/var/log/icecast /usr/local/share/icecast/ 

# 3. Exposer le port 8000
EXPOSE 8000

# 4. Définir la commande de lancement : PAS le script /etc/init.d/icecast2
#    (celui-là fait le changeowner qui te pose problème) — lance
#    directement le binaire icecast2 en foreground avec l'option -c
#    pointant vers ton fichier de config

USER icecast2

RUN cp -r /usr/share/icecast2/* /usr/local/share/icecast/
CMD ["icecast2", "-c", "/etc/icecast2/icecast.xml"]
