# Lito TTS Strategy & Business Plan

*Created: December 24, 2024*

---

## Executive Summary

Lito is a **free, open-source text-to-speech application** offering both a web demo and desktop app. Our strategy uses a hybrid TTS approach to remain **legally compliant, sustainable, and competitive**.

| Platform | TTS Provider | Cost | Limit |
|----------|--------------|------|-------|
| **Web** | Google Cloud TTS | Free tier (4M chars/month) | 10,000 chars/conversion |
| **Desktop** | edge-tts | $0 | Unlimited |

---

## Problem Statement

### Business Challenges
1. **Sustainability**: Offering unlimited free TTS on the web creates unpredictable costs
2. **Legal Risk**: edge-tts uses an unofficial Microsoft API (ToS gray area for public services)
3. **Reliability**: Unofficial APIs can break without warning

### Competitive Landscape

| Competitor | Free Limit | MP3 Export | Notes |
|------------|------------|------------|-------|
| NaturalReader | 4K-20K chars/day | ❌ | Premium features paywalled |
| TTSReader | Unlimited (basic voices) | ⚠️ Personal only | No commercial audio export |
| **Lito (Our Solution)** | 10K chars (~3 pages) | ✅ Yes | Generous + desktop unlimited |

---

## Solution: "Demo → Download" Funnel

### User Journey
```
┌─────────────────────────────────────────────────────────────┐
│  USER DISCOVERS LITO WEB                                    │
│  ↓                                                          │
│  Tries demo (up to 10,000 characters, ~3 pages)             │
│  ↓                                                          │
│  Gets high-quality audio with free MP3 download             │
│  ↓                                                          │
│  If needs more → CTA: "Download Desktop for Unlimited"      │
│  ↓                                                          │
│  Desktop app = edge-tts (personal use, legal, unlimited)    │
└─────────────────────────────────────────────────────────────┘
```

### Why This Works
1. **Low friction entry**: Web demo requires no download
2. **Generous demo**: 10K chars beats most competitors' free tiers
3. **Sustainable**: Google Cloud free tier covers ~400 demos/month
4. **Power users served**: Desktop app = truly unlimited
5. **Legally sound**: Web uses official API, desktop is personal use

---

## Technical Architecture

### Web App (Demo)
- **Frontend**: HTML/CSS/JS on Vercel
- **Backend**: FastAPI on Vercel Serverless
- **TTS**: Google Cloud Text-to-Speech API
- **Limit**: 10,000 characters per conversion

### Desktop App (Full)
- **Framework**: Python + Tkinter
- **TTS**: edge-tts (Microsoft Edge's offline TTS)
- **Distribution**: GitHub Releases (standalone .exe)
- **Limit**: None (runs on user's machine)

---

## Cost Analysis

### Current (Free Tier)
| Component | Monthly Cost |
|-----------|--------------|
| Vercel Hosting | $0 |
| Google Cloud TTS (4M chars) | $0 |
| **Total** | **$0** |

### Scaling Scenarios

| Daily Users | Monthly Chars | Google Cost | Notes |
|-------------|---------------|-------------|-------|
| 10 | 100K | $0 | Well within free tier |
| 100 | 1M | $0 | Still free |
| 400 | 4M | $0 | At free tier limit |
| 1,000 | 10M | ~$24 | 6M overage × $4 |
| 10,000 | 100M | ~$384 | Consider self-hosted TTS |

---

## Implementation Phases

### Phase 1: Web App Migration (Current)
- [ ] Set up Google Cloud TTS API
- [ ] Replace edge-tts with Google Cloud in web backend
- [ ] Add 10,000 character limit
- [ ] Add character counter UI
- [ ] Add download CTA banner
- [ ] Update messaging to "Demo"

### Phase 2: Polish (If Traction)
- [ ] Add IP-based rate limiting (Vercel KV)
- [ ] Analytics for usage monitoring
- [ ] Improve download page/onboarding

### Phase 3: Scale (If High Volume)
- [ ] Evaluate self-hosted TTS (Coqui XTTS-v2)
- [ ] Consider sponsorships/donations
- [ ] CDN for audio caching

---

## Legal Considerations

### edge-tts (Desktop)
- Uses reverse-engineered Microsoft Edge API
- ✅ **Acceptable for personal use** (user's own machine)
- ❌ Not recommended for commercial web services

### Google Cloud TTS (Web)
- ✅ Official API with clear terms
- ✅ Commercial use allowed with subscription
- Free tier = 4M chars/month

---

## Key Decisions Made

1. **Why not edge-tts for web?**
   - Legal gray area for public services
   - API can break without warning
   - Microsoft explicitly states "personal use only"

2. **Why not self-hosted open-source TTS?**
   - Vietnamese voice quality not comparable
   - GPU hosting costs exceed API costs at low volume
   - Maintenance overhead for hobby project

3. **Why 10,000 character limit?**
   - ~3 pages / ~2,000 words / ~8-10 min audio
   - More generous than NaturalReader Plus (4K)
   - Enough for typical articles, not enough for abuse

---

## Future Considerations

### If API Costs Become Significant
1. Reduce character limit (8K → 5K)
2. Implement daily per-IP limits
3. Add "priority" donation tier
4. Migrate to self-hosted Coqui XTTS-v2

### If edge-tts Breaks
Desktop app would need migration to:
- pyttsx3 (offline, lower quality)
- Google Cloud TTS (costs for users)
- Self-hosted model

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Web demo conversions | Track monthly |
| Desktop downloads | Growing MoM |
| API cost | < $10/month |
| User complaints | Near zero |
