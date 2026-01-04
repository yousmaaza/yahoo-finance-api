# Yahoo Finance API Service

API FastAPI utilisant `yfinance` pour fournir des données financières aux workflows n8n.

## 🎯 Objectif

Fournir une API stable et fiable pour récupérer les données Yahoo Finance sans gérer manuellement le système de crumb/cookies de Yahoo. Le package `yfinance` gère automatiquement toute l'authentification.

## ✨ Fonctionnalités

- ✅ **Données fondamentales** : P/E, P/B, ROE, ROA, dividendes, dette, etc.
- ✅ **Données historiques** : Prix OHLCV sur différentes périodes
- ✅ **Cotations en temps réel** : Dernier prix disponible
- ✅ **Gestion automatique du crumb** : yfinance gère l'authentification Yahoo
- ✅ **Documentation interactive** : Swagger UI intégré

## 🚀 Démarrage rapide

### Option 1 : Docker Compose (Recommandé)

```bash
# Build et démarrer le service
docker-compose up -d --build

# Vérifier les logs
docker-compose logs -f

# Arrêter le service
docker-compose down
```

### Option 2 : Installation locale

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
python main.py

# Ou avec uvicorn directement
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## 📖 API Endpoints

### Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "timestamp": "2026-01-04T15:30:00"
}
```

### Données Fondamentales

**GET** `/api/fundamentals/{ticker}`

Exemple : `/api/fundamentals/MC.PA` (LVMH)

```json
{
  "ticker": "MC.PA",
  "name": "LVMH Moët Hennessy - Louis Vuitton",
  "date": "2026-01-04",
  "pe_ratio": 25.3,
  "pb_ratio": 5.2,
  "ps_ratio": 3.8,
  "peg_ratio": 1.5,
  "roe": 18.5,
  "roa": 12.3,
  "profit_margin": 21.2,
  "dividend_yield": 1.8,
  "dividend_per_share": 12.0,
  "payout_ratio": 45.0,
  "revenue_growth": 8.5,
  "earnings_growth": 12.0,
  "debt_to_equity": 0.35,
  "current_ratio": 1.8,
  "beta": 1.1,
  "analyst_rating": "buy",
  "success": true
}
```

### Données Historiques

**GET** `/api/historical/{ticker}?period=1y&interval=1d`

Paramètres :
- `period` : 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
- `interval` : 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

Exemple : `/api/historical/MC.PA?period=1y&interval=1d`

```json
{
  "ticker": "MC.PA",
  "period": "1y",
  "interval": "1d",
  "data": [
    {
      "date": "2025-01-04",
      "open": 720.5,
      "high": 725.3,
      "low": 718.2,
      "close": 723.8,
      "volume": 1250000,
      "adjusted_close": 723.8
    }
  ],
  "success": true
}
```

### Cotation Actuelle

**GET** `/api/quote/{ticker}`

Exemple : `/api/quote/MC.PA`

```json
{
  "ticker": "MC.PA",
  "date": "2026-01-04",
  "open": 720.5,
  "high": 725.3,
  "low": 718.2,
  "close": 723.8,
  "volume": 1250000,
  "adjusted_close": 723.8,
  "success": true
}
```

## 🔧 Intégration avec n8n

### Configuration dans n8n

1. **URL du service** : `http://yahoo-finance-api:5000` (si dans le même réseau Docker)
2. **URL locale** : `http://localhost:5000` (si n8n est hors Docker)

### Exemple de node HTTP Request dans n8n

**Pour les données fondamentales** :

```json
{
  "url": "http://yahoo-finance-api:5000/api/fundamentals/{{ $json.ticker }}",
  "method": "GET",
  "options": {
    "timeout": 30000
  }
}
```

**Pour les données historiques** :

```json
{
  "url": "http://yahoo-finance-api:5000/api/historical/{{ $json.ticker }}?period=1y&interval=1d",
  "method": "GET",
  "options": {
    "timeout": 30000
  }
}
```

## 📚 Documentation Interactive

Une fois le service démarré, accédez à :

- **Swagger UI** : http://localhost:5000/docs
- **ReDoc** : http://localhost:5000/redoc

## 🐛 Troubleshooting

### Service ne démarre pas

```bash
# Vérifier les logs
docker-compose logs yahoo-finance-api

# Vérifier que le port 5000 n'est pas déjà utilisé
lsof -i :5000
```

### Erreurs de connexion depuis n8n

**Si n8n est dans Docker** :
- Utiliser `http://yahoo-finance-api:5000` (nom du service Docker)
- S'assurer que les deux services sont sur le même réseau Docker

**Si n8n est local** :
- Utiliser `http://localhost:5000`

### Données manquantes pour certains tickers

Certains tickers peuvent ne pas avoir toutes les données disponibles. L'API retournera `null` pour les champs manquants.

## 🔒 Sécurité

- ⚠️ **Ne pas exposer publiquement** : Ce service est prévu pour un usage interne uniquement
- ⚠️ **Rate limiting** : Yahoo Finance peut limiter les requêtes, considérer l'ajout d'un cache
- ⚠️ **Authentification** : Ajouter une authentification si besoin (API key, JWT, etc.)

## 📝 Notes

- **yfinance** gère automatiquement le crumb et les cookies Yahoo Finance
- Les pourcentages (ROE, ROA, etc.) sont automatiquement convertis en pourcentage (0.15 → 15.0)
- Les prix sont arrondis à 4 décimales
- Les volumes sont retournés en entiers

## 🚀 Améliorations futures

- [ ] Ajout d'un système de cache Redis pour réduire les requêtes
- [ ] Rate limiting par IP/token
- [ ] Authentification par API key
- [ ] Support de batch requests (plusieurs tickers en une fois)
- [ ] Logs structurés (JSON)
- [ ] Métriques Prometheus

## 📖 Documentation yfinance

- GitHub : https://github.com/ranaroussi/yfinance
- PyPI : https://pypi.org/project/yfinance/

## 📄 Licence

MIT

---

**Version** : 1.0.0
**Dernière mise à jour** : 4 janvier 2026
