export default function About() {
    const team = [
        { icon: "🤖", title: "AI-Powered", text: "A fine-tuned MobileNetV2 deep learning model classifies your body type from a single photo." },
        { icon: "🎯", title: "Personalised", text: "Recommendations are 100% tailored to YOUR body shape — ectomorph, mesomorph, or endomorph." },
        { icon: "🛍️", title: "Shop Ready", text: "Every suggestion links directly to Amazon & Flipkart so you can buy instantly." },
        { icon: "🔒", title: "Privacy First", text: "Your uploaded photo is processed in real-time and never stored permanently on our servers." },
    ];

    return (
        <main className="container fade-in" style={{ marginTop: "90px", paddingBottom: "4rem" }}>
            <div className="page-section">
                <h1>About <span className="text-gradient">WearWisely</span></h1>
                <p className="lead">
                    WearWisely is a smart, body-type-aware fashion recommendation engine built for men.
                    Simply upload a photo — our AI handles the rest, telling you exactly which styles
                    suit your unique physique and pointing you straight to the shopping cart.
                </p>

                <div className="info-grid">
                    {team.map((item, i) => (
                        <div className="info-card" key={i} style={{ animationDelay: `${i * 0.08}s` }}>
                            <div className="info-icon">{item.icon}</div>
                            <h3>{item.title}</h3>
                            <p>{item.text}</p>
                        </div>
                    ))}
                </div>

                <div className="glass-card" style={{ marginTop: "2.5rem" }}>
                    <h2 style={{ margin: "0 0 1rem" }}>🧠 The Technology</h2>
                    <p style={{ color: "var(--text-dim)", lineHeight: "1.8", margin: 0 }}>
                        The core model is a fine-tuned <strong style={{ color: "var(--text-light)" }}>MobileNetV2</strong> trained
                        on a balanced dataset of ectomorph, mesomorph, and endomorph body types with transfer learning,
                        data augmentation, and class-weight balancing for optimal accuracy.
                        The backend is powered by <strong style={{ color: "var(--text-light)" }}>FastAPI</strong> + <strong style={{ color: "var(--text-light)" }}>TensorFlow</strong>.
                        The frontend is built in <strong style={{ color: "var(--text-light)" }}>React + Vite</strong>.
                    </p>
                </div>
            </div>
        </main>
    );
}
