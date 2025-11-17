# 🧠 Botfusions Memori API

AI Memory API Service powered by Memori SDK

## 🚀 Quick Deploy (Coolify)

### Environment Variables
```bash
MEMORI_DATABASE__CONNECTION_STRING=postgresql://postgres:PASSWORD@supabase-db-d0cso0goco0swwcgc4gkgw8c:5432/postgres
OPENAI_API_KEY=sk-...
MEMORI_MEMORY__NAMESPACE=botfusions_production
MEMORI_AGENTS__OPENAI_API_KEY=${OPENAI_API_KEY}
```

### Deploy
1. Coolify → New Service → Public Repository
2. URL: `https://github.com/botfusions/memory.git`
3. Port: `8002`
4. Domain: `memori.turklawai.com`
5. Add Environment Variables
6. Deploy!

## 📡 API Endpoints

- `GET /health` - Health check
- `POST /chat` - Chat with memory
- `GET /memory/stats` - Memory statistics
- `GET /docs` - Swagger UI

## 📞 Contact

**Botfusions**
- Email: info@botfusions.com
- Tel: +90 850 302 74 60
