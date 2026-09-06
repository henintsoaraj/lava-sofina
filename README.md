# 🎙️ Lava Sofina — Radio en ligne avec DJ IA

Une radio en streaming complète, construite de zéro comme projet d'apprentissage DevOps : diffusion audio en direct, un DJ animé par IA qui intervient avec la météo réelle, une API "now playing", et une interface web — le tout conteneurisé, orchestré par Kubernetes, et déployé en HTTPS sur un vrai serveur cloud.

**🔴 Écouter en direct :** [https://tsoum-radio.duckdns.org](https://tsoum-radio.duckdns.org)

---

## Ce que fait ce projet

- Diffuse un flux audio en continu (Icecast + Liquidsoap), à partir d'une playlist de musique
- Un DJ IA (Google Gemini + Edge TTS) génère automatiquement, toutes les 2 heures, une courte intervention vocale annonçant la météo réelle du moment, insérée en priorité entre deux morceaux
- Une API expose le morceau en cours et le nombre d'auditeurs
- Une page web affiche ces informations en direct
- Tout tourne en HTTPS, derrière un seul nom de domaine

## Architecture

```
                         ┌─────────────────────────┐
                         │   tsoum-radio.duckdns.org │  (HTTPS, Let's Encrypt)
                         └───────────┬─────────────┘
                                     │
                              Ingress (Traefik)
                    ┌────────────────┼────────────────┐
                    │                │                 │
                 /  →  web        /now-playing → api   /radio.mp3 → icecast
                    │                │                 │
                 (nginx)         (FastAPI)          (Icecast)
                                     │                 ▲
                                     └──── status ──────┘
                                                        │
                                                   Liquidsoap
                                                   (playlist + file DJ)
                                                        ▲
                                                        │
                                              DJ IA (CronJob, /2h)
                                        Gemini → texte → Edge TTS → audio
                                                        │
                                              Open-Meteo (météo réelle)
```

Cinq services, chacun dans son propre conteneur, communiquant via le réseau interne Kubernetes :

| Service      | Rôle                                            | Techno                    |
|--------------|--------------------------------------------------|----------------------------|
| `icecast`    | Serveur de streaming, diffuse le flux audio      | Icecast 2 (Ubuntu)         |
| `liquidsoap` | Lit la playlist, gère la priorité DJ vs musique  | Liquidsoap 2.0.3 (savonet) |
| `api`        | Expose le morceau en cours et le nb d'auditeurs  | FastAPI (Python)           |
| `dj-ia`      | Génère et pousse les interventions vocales       | Python (Gemini + Edge TTS) |
| `web`        | Interface web "now playing"                       | HTML/CSS/JS + nginx        |

## Stack technique

- **Conteneurisation :** Docker, images multi-architecture (amd64/arm64)
- **Orchestration :** Kubernetes (K3s en production, Minikube en développement)
- **CI/CD :** GitHub Actions — build, test d'intégration, publication sur GitHub Container Registry
- **HTTPS :** cert-manager + Let's Encrypt, Ingress Traefik
- **Hébergement :** Oracle Cloud (Always Free tier, ARM)
- **IA :** Google Gemini (génération de texte), Edge TTS (synthèse vocale)
- **Données externes :** Open-Meteo (météo, sans clé API)

## Lancer le projet en local

Le projet tourne aussi en local avec Docker Compose, pour développer sans dépendre du cluster de production.

### Prérequis

- Docker et Docker Compose installés
- Une clé API Google Gemini (gratuite sur [Google AI Studio](https://aistudio.google.com))

### Étapes

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/henintsoaraj/lava-sofina.git
   cd lava-sofina
   ```

2. Créez votre fichier de configuration Icecast à partir du modèle fourni :
   ```bash
   cp icecast/icecast.xml.example icecast/icecast.xml
   ```
   Éditez `icecast/icecast.xml` et choisissez votre propre mot de passe source.

3. Définissez ce même mot de passe comme variable d'environnement :
   ```bash
   export ICECAST_SOURCE_PASSWORD="votre_mot_de_passe"
   ```

4. Ajoutez quelques fichiers `.mp3` dans `liquidsoap/music/` (playlist de test).

5. Lancez tout :
   ```bash
   docker compose up -d
   ```

6. Écoutez le flux : [http://localhost:8000/radio.mp3](http://localhost:8000/radio.mp3)
   Consultez l'API : [http://localhost:8001/now-playing](http://localhost:8001/now-playing)

Le service `dj-ia` (CronJob en production) n'est pas inclus dans le `docker-compose.yml` — il nécessite une clé Gemini et est pensé pour tourner sur Kubernetes ; voir `k8s/dj-ia-cronjob.yaml` pour l'exécuter manuellement en local si besoin.

## Déploiement Kubernetes

Les manifests complets se trouvent dans `k8s/`. Quelques objets doivent être créés manuellement (secrets, ConfigMap) avant d'appliquer les fichiers YAML — ils ne sont jamais versionnés :

```bash
kubectl create secret generic icecast-password --from-literal=ICECAST_SOURCE_PASSWORD=...
kubectl create secret generic gemini-api-key --from-literal=GEMINI_API_KEY=...
kubectl create configmap liquidsoap-script --from-file=script.liq=liquidsoap/script.liq

kubectl apply -f k8s/
```

Pour l'Ingress HTTPS, copiez et adaptez `k8s/cluster-issuer-prod.yaml.example` avec votre propre email, avant de l'appliquer.

## Ce que ce projet m'a appris

Ce projet a été construit pas à pas comme exercice DevOps complet : Docker et permissions Linux, Docker Compose, Git et gestion des secrets, CI/CD avec GitHub Actions, Kubernetes (Deployment, Service, ConfigMap, Secret, PersistentVolumeClaim, CronJob), déploiement multi-architecture, et enfin HTTPS avec cert-manager sur un vrai serveur cloud (Oracle Cloud, K3s).
