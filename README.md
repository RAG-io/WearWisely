# WearWisely 👔

WearWisely is a smart, body-type-aware fashion recommendation engine built exclusively for men. By simply uploading a full-body photo, our fine-tuned Deep Learning model classifies your body type (Ectomorph, Mesomorph, or Endomorph) and provides 100% personalized clothing styles and complete outfit combinations curated for your unique physique.

## ✨ Features
- **AI Body Type Classification:** Powered by a MobileNetV2 architecture trained via transfer learning to accurately detect body proportions from a single image.
- **Tailored Recommendations:** Suggests specific clothing items (from casual to formal) that flatter your exact body type, complete with real product images.
- **Curated Outfits:** Pre-built, head-to-toe "Complete the Look" combos.
- **Direct Shopping Integrations:** Instant links to purchase recommended items directly on Amazon and Flipkart.
- **Privacy-First:** Images are processed in real-time in memory and never stored.

## 🏗️ Project Architecture
This repository is structured as a modern full-stack web application integrated natively with our deep learning pipeline:

- `src/` & `public/`: Modern React + Vite frontend UI with dark/light mode support.
- `backend/`: High-performance FastAPI backend server serving predictions and logic.
- `dl/`: Deep Learning tracking directory containing our datasets, TF/Keras model weights, data augmentation scripts, and training/evaluation pipelines.

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- `pip` or virtual environment utilities

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/wearwisely.git
   cd wearwisely
   ```
2. **Setup Frontend:**
   ```bash
   npm install
   ```
3. **Setup Backend & DL Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

### Running Locally
To run the project, open two separate terminal instances from the root directory:

**Terminal 1 (Backend API):**
```bash
source .venv/bin/activate
python3 -m uvicorn backend.main:app --reload
```

**Terminal 2 (Frontend UI):**
```bash
npm run dev
```
Navigate to `http://localhost:5173` to interact with WearWisely!

## 🚧 Status & Future Work
**Status:** Active Development. The core prediction engine, API, and React frontend are fully functional and integrated into a unified production-ready monorepo structure.

**Upcoming Enhancements (WIP):**
- Dynamic image caching and CDN optimization for the recommended product visuals.
- Expanding the recommendation engine database for seasonal and trend-specific outfits.
- Hardening the FastAPI CORS configuration and adding production-grade error handling.
- Dockerizing the application for seamless deployment.
- Mobile-responsive UI polish and continuous accessibility audits.
