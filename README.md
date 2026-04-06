# WearWisely

WearWisely is a smart, body-type-aware fashion recommendation engine built exclusively for men. By simply uploading a full-body photo, our fine-tuned Deep Learning model classifies your body type (Ectomorph, Mesomorph, or Endomorph) and provides 100% personalized clothing styles and complete outfit combinations curated for your unique physique.

## ✨ Features
- **AI Body Type Classification:** Powered by a MobileNetV2 architecture trained via transfer learning to accurately detect body proportions from a single image.
- **Ultra-Premium Glassmorphic UI:** Features cinematic wide-screen dashboards, flawless light/dark mode frosted glass, drifting ambient background orbs, and dynamic hacker-typing text sequences.
- **Virtual Fitting Room (VTON):** Deep integration with `yisol/IDM-VTON` via Hugging Face API to seamlessly superimpose recommended clothing directly onto your uploaded photo while preserving your actual face and body proportions.
- **3D Parallax Interactions:** Product cards and the virtual stage utilize advanced 3D tilting mechanics, tracking cursor movements and reflecting dynamic glass glare.
- **Dynamic Lookbooks & Filtering:** Filter recommendations by occasion (Casual, Formal, Office, Party) and view complete head-to-toe curated outfit combos.
- **Direct Shopping Integrations:** Instant links to purchase recommended items directly on Amazon and Flipkart.
- **ZeroGPU Resiliency:** Custom intelligent retry-loops ensure Virtual Try-On requests survive transient traffic spikes on global Hugging Face servers.

## 👕 Virtual Fitting Room (VTON) Engine
WearWisely features a state-of-the-art Virtual Fitting Room powered by the `yisol/IDM-VTON` model hosted on Hugging Face. After the AI analyzes your body type, simply click **"Try It On"** on any recommended garment to see exactly how it looks on your uploaded photo.

**How it works:**
1. The backend securely extracts the garment image from the dataset and pairs it with your uploaded photo.
2. It sends a generated composite to the Hugging Face API to run the high-fidelity IDM-VTON diffusion model.
3. The API is specifically configured to preserve your actual face, head, and legs, naturally molding the new garment onto your torso.
4. **ZeroGPU Auto-Retry:** Hugging Face servers can experience heavy global traffic. If a "No GPU Available" timeout occurs, our backend will silently wait 5 seconds and automatically retry up to 3 times, guaranteeing your image generates seamlessly.

> **⚠️ Important Notice (`HF_TOKEN`):**
> While the Try-On feature works anonymously, you will quickly hit rate limits. To unlock unlimited generations, you must pass a Hugging Face Access Token when starting the backend server (see the *Running Locally* section).

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
# Highly recommended: Pass your HF_TOKEN to unlock unlimited Virtual Try-Ons
HF_TOKEN="your_hugging_face_token_here" python3 -m uvicorn backend.main:app --reload
```

**Terminal 2 (Frontend UI):**
```bash
npm run dev
```
Navigate to `http://localhost:5173` to interact with WearWisely!
