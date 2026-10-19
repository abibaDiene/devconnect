# DevConnect — prototype frontend + backend MVP

Application communautaire pour développeurs, interface Dark Tech.

## Prérequis
- Docker Desktop + Docker Compose
- Node.js 20+ et npm

## Démarrage local
1. Depuis `devconnect/`, exécuter `cp .env.example .env` (Windows PowerShell : `Copy-Item .env.example .env`). Ajuster les secrets locaux.
2. Exécuter `docker compose build`.
3. **Première installation :** `docker compose run --rm backend python manage.py makemigrations accounts community`.
4. Exécuter `docker compose up -d` (l'API écoute sur http://localhost:8000/api/).
5. Dans un autre terminal : `cd frontend && npm install && npm run dev`.
6. Ouvrir http://localhost:5173.

Le frontend utilise les **API Django**. La phase 6 ajoute les commentaires, réponses, validation d’une réponse et candidatures aux projets.

## Interactions intégrées (phase 6)
- Publication : ouvrir les commentaires et ajouter un commentaire connecté.
- Question : afficher les réponses, publier une réponse et accepter une réponse (auteur uniquement).
- Projet : cocher « Je recherche des collaborateurs » à la création, candidater, accepter/refuser côté propriétaire.
- Les opérations affichent les erreurs API et rechargent les données depuis Django.

## API disponibles
- `GET /api/auth/csrf/` : initialise le cookie CSRF
- `POST /api/auth/register/` : compte `{username,email,password}`
- `POST /api/auth/login/` : session `{username,password}`
- `POST /api/auth/logout/` : déconnexion
- `GET/PATCH /api/auth/me/` : son profil
- `GET /api/users/?search=...` : membres publics
- `GET/POST /api/posts/` : publications
- `GET/POST /api/posts/{id}/comments/` : commentaires
- `POST /api/posts/{id}/react/` : ajouter/retirer une réaction
- `GET/POST /api/questions/` : questions
- `GET/POST /api/answers/?question=id` : réponses
- `POST /api/questions/{id}/accept_answer/` : corps `{answer_id}`
- `GET/POST /api/projects/` : projets
- `GET/POST /api/applications/` : candidatures
- `POST /api/applications/{id}/decide/` : corps `{status:"accepted"}` ou `{status:"rejected"}`
- `GET/POST /api/reports/` : signalements

Les ressources disposent de routes détail et de modification selon les permissions et la méthode autorisée. Les listes utilisent une pagination avec `results`.

## Authentification et sécurité
Authentification par **session Django** avec cookie HttpOnly. Pour chaque requête POST/PATCH/DELETE depuis le navigateur : appeler d'abord `/api/auth/csrf/`, puis envoyer `X-CSRFToken` avec le cookie `csrftoken`, et utiliser `credentials: 'include'`. Les écritures sont protégées par CSRF. Les rôles restent développeur / admin Django.

## Tests
`docker compose exec backend python manage.py test`

## Restrictions de cette livraison
- Docker Compose utilise `runserver` et DEBUG=true **uniquement pour le développement local**.
- Configuration production HTTPS, secrets, hôtes, cookies, médias, migrations versionnées, sauvegardes et contrôle des permissions supplémentaires à finaliser avant tout déploiement public.
- Les migrations sont générées au premier lancement (pas encore incluses dans cette archive).
- Cette archive n'a pas été validée par un lancement Docker / tests Django dans cet environnement.

## Phase 5 — Intégration frontend/API

Le frontend utilise maintenant les endpoints Django réels pour : inscription, connexion, déconnexion, lecture/modification du profil, création/lecture des publications, réactions, questions, projets, et consultation de la communauté. Les anciennes données de démonstration ne sont plus utilisées. La liste est paginée côté API (première page actuellement) ; commentaires, réponses et candidatures nécessitent encore leurs formulaires frontend.

### Démarrage local

1. Copier `.env.example` vers `.env` et modifier le secret.
2. `docker compose build`
3. **Créer les migrations des deux applications** : `docker compose run --rm backend python manage.py makemigrations accounts community`
4. `docker compose up -d`
5. Dans un second terminal : `cd frontend && npm install && npm run dev`
6. Ouvrir **http://localhost:5173** (utiliser `localhost`, et non `127.0.0.1`, pour conserver le même domaine de cookies).

Vite fait suivre `/api` à Django sur le port 8000, ce qui évite les appels cross-origin en développement. Le navigateur envoie les cookies de session ; les requêtes de mutation incluent un jeton CSRF. N'exposez pas cette configuration Docker de développement sur Internet.

### Limitations actuelles

La compilation, le démarrage Docker et les tests d'intégration ne sont pas garantis dans l'environnement de création. Les migrations ne sont pas incluses dans l'archive : la commande `makemigrations` ci-dessus est nécessaire une seule fois, avant le premier `up`. Compléter également les formulaires réponses/commentaires/candidatures, les contrôles de validation, la pagination et les tests avant déploiement.

## Phase 7 — Recherche et filtres avancés

- Barre de recherche serveur (temporisation de 350 ms) dans Publications, Questions, Projets et Communauté.
- Questions : mots-clés, statut résolu/non résolu, tri chronologique. API facultative `tag=django` (correspondance exacte).
- Projets : mots-clés, recrutement ouvert/fermé, tri chronologique. API facultative `technology=Django` (correspondance exacte).
- Communauté : nom, bio, localisation ; compétence exacte ; tri alphabétique ou par inscription.
- L'interface parcourt les pages de l'API pour ne pas limiter les recherches aux 20 premiers résultats. Pour un catalogue très important, introduire plus tard une pagination visible ou un défilement infini.
- Aucune migration supplémentaire nécessaire (modèles inchangés).

Pour tester : `docker compose up -d --build` puis `docker compose exec backend python manage.py test tests_api` et `cd frontend && npm install && npm run build && npm run dev`.

Note : recherche de tags/technologies accessible côté API mais sans champ dédié dans l'interface pour cette version ; les recherches de compétences utilisent une correspondance exacte et sensible à la casse dans le champ `skills` JSON. Une normalisation des compétences/tags est recommandée ensuite.


## Phase 8 — Modération

- Membres connectés : bouton **Signaler** sur publications et questions.
- Administrateurs (`is_staff=True`) : onglet **Modération**, liste des signalements, masquage ou rejet.
- Les contenus masqués ne sont plus exposés aux membres ni aux visiteurs (les administrateurs peuvent encore les voir).
- Gestion des utilisateurs (désactivation) via l'administration Django `/admin/`; endpoint staff `POST /api/users/{id}/set_active/` avec `{"is_active": false}`.
- Les nouveaux champs `is_hidden` nécessitent une migration.

### Mise à jour depuis la version précédente

Sauvegarder le projet et la base avant de remplacer des fichiers, puis exécuter :

```powershell
docker compose up -d --build
docker compose exec backend python manage.py makemigrations community
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

La commande `createsuperuser` est à exécuter uniquement si aucun compte administrateur n'existe.

Depuis `frontend` : `npm install`, `npm run build`, puis `npm run dev`.

**Attention** : le développement n'a pas été validé de bout en bout en conteneurs ici.


## Phase 9 et 10 — Sécurité, tests, UI mobile

- Connexion et inscription protégées contre CSRF (le frontend initialise le cookie `/api/auth/csrf/`).
- Limitation globale du débit des requêtes API et limitation renforcée connexion/inscription (en mémoire/cache local par défaut : utiliser Redis ou autre cache partagé en production).
- Interdiction de commenter une publication masquée ou répondre à une question masquée.
- Tests des autorisations, de la modération et du CSRF dans `backend/tests_security.py`.
- Menu ouvrable au mobile, fermeture via un bouton/voile ; états de chargement, focus visible, contraste et support `prefers-reduced-motion`.

### Vérifications (depuis la racine)

```powershell
docker compose up -d --build
docker compose exec backend python manage.py check
docker compose exec backend python manage.py test tests_api tests_security
cd frontend
npm install
npm run build
npm run dev
```

Attention : cette livraison n'est pas une validation de sécurité de production. À terminer avant l'ouverture : tests E2E navigateur, audit de dépendances, journalisation, vraie politique de sauvegarde, service ASGI/WSGI de production, proxy HTTPS et stockage de cache partagé pour les limites de débit.
