# 🤖 Bot Telegram de Fact-Checking

Bot Telegram intelligent capable de vérifier les affirmations factuelles dans différents types de contenus (texte, images, vidéos, audio, liens).

## 🌟 Fonctionnalités

- ✅ **Analyse de texte** - Détection automatique d'affirmations factuelles
- 🖼️ **OCR sur images** - Extraction de texte depuis des images
- 🎬 **Transcription vidéo** - Analyse audio et visuelle des vidéos
- 🎵 **Transcription audio** - Conversion de notes vocales en texte
- 🔗 **Extraction web** - Analyse de contenu depuis des URLs
- 📄 **Documents** - Support PDF, TXT, DOC, DOCX
- ✅ **Fact-checking** - Vérification via l'API Vera

## 🛠️ Technologies

- **Python 3.11+**
- **python-telegram-bot** - Interface Telegram
- **Google Gemini API** - Analyse multimédia (OCR, transcription, extraction)
- **Vera API** - Vérification factuelle
- **httpx** - Client HTTP asynchrone

## 📋 Prérequis

1. **Python 3.11 ou supérieur**
2. **Clés API** :
   - Token Telegram Bot (via BotFather)
   - Google Gemini API Key
   - Vera API Key

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone <votre-repo>
cd telegram-fact-checker
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Copiez `.env.example` vers `.env` et remplissez les valeurs :

```bash
cp .env.example .env
```

Éditez `.env` :

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
VERA_API_KEY=your_vera_api_key
```

### 5. Créer votre bot Telegram

1. Ouvrez [@BotFather](https://t.me/botfather) sur Telegram
2. Envoyez `/newbot`
3. Suivez les instructions
4. Copiez le token dans `.env`

## 🎯 Utilisation

### Démarrer le bot

```bash
python main.py
```

### Utiliser le bot

1. Ouvrez votre bot sur Telegram
2. Envoyez `/start` pour voir le message de bienvenue
3. Envoyez du contenu à vérifier :
   - Texte avec une affirmation
   - Image contenant du texte
   - Vidéo ou audio
   - Lien vers un article
   - Document PDF/TXT

### Commandes disponibles

- `/start` - Message de bienvenue
- `/help` - Aide détaillée
- `/about` - Informations sur le bot

## 📁 Structure du Projet

```
telegram-fact-checker/
├── config/
│   └── settings.py          # Configuration centralisée
├── handlers/
│   ├── text_handler.py      # Handler texte
│   ├── image_handler.py     # Handler images
│   ├── video_handler.py     # Handler vidéos
│   ├── audio_handler.py     # Handler audio
│   ├── link_handler.py      # Handler liens
│   └── document_handler.py  # Handler documents
├── services/
│   ├── gemini_client.py     # Client Gemini
│   └── vera_client.py       # Client Vera
├── utils/
│   ├── logger.py            # Configuration logging
│   ├── validators.py        # Validations
│   └── formatters.py        # Formatage des réponses
├── models/
│   └── content.py           # Modèles de données
├── main.py                  # Point d'entrée
├── requirements.txt         # Dépendances
└── .env                     # Variables d'environnement
```

## 🔒 Sécurité et Confidentialité

- ✅ Aucune donnée utilisateur n'est stockée
- ✅ Fichiers temporaires supprimés après traitement
- ✅ Logs anonymisés
- ✅ Clés API dans `.env` (jamais committées)
- ✅ Rate limiting pour éviter les abus

## 🐛 Dépannage

### Le bot ne répond pas

1. Vérifiez que le token Telegram est correct
2. Vérifiez les logs dans `logs/bot.log`
3. Testez la connexion réseau

### Erreur "API Key invalide"

1. Vérifiez que les clés API sont correctement copiées dans `.env`
2. Vérifiez qu'il n'y a pas d'espaces avant/après les clés

### Erreur lors de l'analyse

1. Vérifiez que les fichiers sont dans les formats supportés
2. Vérifiez la taille des fichiers (limites dans `.env`)
3. Consultez les logs pour plus de détails

## 📊 Limitations

- **Taille des fichiers** :
  - Images : 10 MB
  - Vidéos : 50 MB
  - Audio : 20 MB
  - Documents : 20 MB

- **Formats supportés** :
  - Images : JPEG, PNG, WebP, GIF
  - Vidéos : MP4, MPEG, QuickTime, AVI
  - Audio : MP3, OGG, WAV, MP4
  - Documents : PDF, TXT, DOC, DOCX

## 🤝 Contribution

Les contributions sont les bienvenues ! Merci de :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -am 'Ajout d'une fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

## 🙏 Remerciements

- [Google Gemini](https://ai.google.dev/) - Analyse multimédia
- [Vera API](https://vera.com) - Fact-checking
- [python-telegram-bot](https://python-telegram-bot.org/) - Framework Telegram

## 📞 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.

---

**Développé avec ❤️ pour lutter contre la désinformation**