export default function HowItWorks() {
    const steps = [
        { num: "1", icon: "📸", title: "Upload a Photo", text: "Take or choose a clear, full-body photo of yourself in good lighting. Stand straight against a plain wall for best results." },
        { num: "2", icon: "🤖", title: "AI Analyses Your Body", text: "Our MobileNetV2 model classifies your body type with a confidence score in seconds." },
        { num: "3", icon: "👔", title: "Get Recommendations", text: "Receive a curated list of clothing items and complete outfit combos best suited to your body shape." },
        { num: "4", icon: "🛒", title: "Shop Instantly", text: "Click Amazon or Flipkart links on any item to buy it directly — no extra search needed." },
    ];

    const tips = [
        { icon: "💡", text: "Use a plain, light background" },
        { icon: "📏", text: "Stand straight, face the camera" },
        { icon: "☀️", text: "Good natural or indoor lighting" },
        { icon: "👕", text: "Wear fitted clothing for accuracy" },
    ];

    return (
        <main className="container fade-in" style={{ marginTop: "90px", paddingBottom: "4rem" }}>
            <div className="page-section">
                <h1>How <span className="text-gradient">It Works</span></h1>
                <p className="lead">
                    Four simple steps from photo to wardrobe — powered entirely by AI.
                </p>

                <div className="steps-grid">
                    {steps.map((s, i) => (
                        <div className="step-card" key={i} style={{ animationDelay: `${i * 0.1}s` }}>
                            <div className="step-num">{s.num}</div>
                            <div style={{ fontSize: "1.6rem", marginBottom: "0.6rem" }}>{s.icon}</div>
                            <h3>{s.title}</h3>
                            <p>{s.text}</p>
                        </div>
                    ))}
                </div>

                <div className="glass-card">
                    <h3 style={{ margin: "0 0 1.2rem", color: "var(--secondary-color)" }}>📸 Photo Tips</h3>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: "1rem" }}>
                        {tips.map((t, i) => (
                            <div key={i} style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--text-dim)", fontSize: "0.9rem" }}>
                                <span style={{ fontSize: "1.3rem" }}>{t.icon}</span>
                                {t.text}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </main>
    );
}
