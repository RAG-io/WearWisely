import React, { useState } from "react";
import axios from "axios";
import Tilt from "react-parallax-tilt";
import BodyTypeCard from "./BodyTypeCard";

/* ── Occasion colour map ── */
const OCCASION_COLOR = {
    All: "var(--secondary-color)",
    Casual: "#74b9ff",
    Formal: "#a29bfe",
    Office: "#55efc4",
    Party: "#fd79a8",
    "Date Night": "#e17055",
};

/* ── SVG Confidence Gauge ── */
function ConfidenceGauge({ value }) {
    const pct = value * 100;
    const color = pct < 60 ? "#fdcb6e" : pct < 85 ? "#74b9ff" : "#55efc4";
    const cls = pct < 60 ? "gauge-low" : pct < 85 ? "gauge-mid" : "gauge-high";

    // Half-circle arc
    const r = 38, cx = 45, cy = 48;
    const circumference = Math.PI * r;           // half-circle
    const offset = circumference * (1 - value);  // remaining arc

    return (
        <div className="confidence-gauge-wrap">
            <div className="gauge-svg-wrap" style={{ width: 90, height: 58 }}>
                <svg width="90" height="58" viewBox="0 0 90 58">
                    {/* Track */}
                    <path
                        d={`M 7 ${cy} A ${r} ${r} 0 0 1 83 ${cy}`}
                        fill="none"
                        stroke="rgba(255,255,255,0.08)"
                        strokeWidth="7"
                        strokeLinecap="round"
                    />
                    {/* Fill arc */}
                    <path
                        d={`M 7 ${cy} A ${r} ${r} 0 0 1 83 ${cy}`}
                        fill="none"
                        stroke={color}
                        strokeWidth="7"
                        strokeLinecap="round"
                        strokeDasharray={`${circumference}`}
                        strokeDashoffset={`${offset}`}
                        style={{ transition: "stroke-dashoffset 0.8s ease" }}
                    />
                </svg>
                <div style={{ position: "absolute", bottom: 0, width: "100%", textAlign: "center" }}>
                    <span className={`gauge-value-text ${cls}`}>{pct.toFixed(0)}%</span>
                </div>
            </div>
            <span className="gauge-label">Confidence</span>
        </div>
    );
}

/* ── Product Image with fallback ── */
function ProductImage({ src, alt }) {
    const [errored, setErrored] = useState(false);
    return (
        <div className="product-img-wrap">
            {errored ? (
                <div className="img-fallback">
                    <span>👔</span>
                    <span>{alt}</span>
                </div>
            ) : (
                <img
                    src={src}
                    alt={alt}
                    onError={() => setErrored(true)}
                    loading="lazy"
                />
            )}
        </div>
    );
}

/* ── Low Confidence Banner ── */
function LowConfidenceBanner() {
    return (
        <div className="low-confidence-banner">
            <span className="lc-icon">⚠️</span>
            <div>
                <strong>Low confidence result.</strong> For best accuracy, use a clear full-body photo with
                good lighting and a plain background — standing straight, facing the camera.
            </div>
        </div>
    );
}

/* ── Main ResultCard ── */
const DOS_DONTS = {
    ectomorph: { dos: ["Layering to add bulk", "Horizontal stripes", "Structured jackets", "Thick fabrics"], donts: ["Oversized, baggy clothes", "Vertical stripes", "Skinny fits", "Monochromatic dark outfits"] },
    endomorph: { dos: ["Vertical stripes", "Darker colors", "V-neck shirts", "Well-tailored straight fits"], donts: ["Horizontal stripes", "Heavy, bulky fabrics", "Tight clothing", "Loud patterns"] },
    mesomorph: { dos: ["Fitted shirts", "Athletic cuts", "V-necks and crew necks", "Straight leg trousers"], donts: ["Excessively baggy clothes", "Super skinny fits", "Ill-fitting shoulders", "Overly tight shirts"] }
};

function ResultCard({ result, userPhotoFile, previewUrl }) {
    const [activeOccasion, setActiveOccasion] = useState("All");
    const [activeTryOn, setActiveTryOn] = useState(null);

    if (!result) return null;

    const handleTryOn = async (item) => {
        if (!userPhotoFile || !item.image) return;

        // Scroll mobile users to the right panel slightly
        if (window.innerWidth < 900) {
            setTimeout(() => {
                document.getElementById("vfr-stage")?.scrollIntoView({ behavior: "smooth", block: "start" });
            }, 100);
        }

        setActiveTryOn({ item, loading: true, image: null });

        try {
            const formData = new FormData();
            formData.append("user_image", userPhotoFile);
            formData.append("garm_url", item.image);

            const res = await axios.post("http://127.0.0.1:8000/try-on", formData);
            setActiveTryOn({ item, loading: false, image: res.data.image_base64 });
        } catch (e) {
            console.error(e);
            alert("Try-On failed: " + (e.response?.data?.detail || e.message));
            setActiveTryOn({ item, loading: false, image: null });
        }
    };

    const recs = result.recommendations?.men ?? [];
    const outfits = result.recommendations?.outfits ?? [];

    const occasions = ["All", ...Array.from(new Set(recs.map((r) => r.occasion).filter(Boolean)))];
    const filteredRecs = activeOccasion === "All"
        ? recs
        : recs.filter((r) => r.occasion === activeOccasion);

    const lowConf = result.confidence < 0.60;

    return (
        <div className="glass-card fade-in advanced-dashboard" style={{ maxWidth: "1400px", width: "95%", margin: "40px auto", textAlign: "left" }}>

            {/* ── HEADER ── */}
            <div className="result-header">
                <h2 style={{ margin: 0, fontSize: "clamp(1.4rem, 3vw, 2.5rem)", letterSpacing: "-0.5px" }}>
                    Body Type:{" "}
                    <span className="text-gradient" style={{ textTransform: "capitalize" }}>
                        {result.body_type}
                    </span>
                </h2>
                <ConfidenceGauge value={result.confidence} />
            </div>

            {/* ── LOW CONFIDENCE WARNING ── */}
            {lowConf && <LowConfidenceBanner />}

            {/* ── BODY TYPE CARDS ── */}
            <div style={{ marginBottom: "2rem" }}>
                <h3 style={{ color: "var(--text-light)", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "10px" }}>
                    <span style={{ color: 'var(--primary-color)' }}>✦</span> Body Type Analysis
                </h3>
                <BodyTypeCard activeType={result.body_type} />

                {/* Advanced Dos and Donts Grid */}
                {DOS_DONTS[result.body_type?.toLowerCase()] && (
                    <div className="dos-donts-grid fade-in">
                        <div className="list-box dos">
                            <h4>✓ What to Wear (Do's)</h4>
                            <ul>
                                {DOS_DONTS[result.body_type.toLowerCase()].dos.map((rule, i) => <li key={i}>{rule}</li>)}
                            </ul>
                        </div>
                        <div className="list-box donts">
                            <h4>✕ What to Avoid (Don'ts)</h4>
                            <ul>
                                {DOS_DONTS[result.body_type.toLowerCase()].donts.map((rule, i) => <li key={i}>{rule}</li>)}
                            </ul>
                        </div>
                    </div>
                )}
            </div>

            {/* ── VIRTUAL FITTING ROOM SPLIT LAYOUT ── */}
            <div className="vfr-container">
                {/* LEFT SIDE: PRODUCTS AND FILTERS */}
                <div className="vfr-left">
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "1rem", marginBottom: "0.5rem" }}>
                        <h3 style={{ color: "var(--text-light)", margin: 0, display: "flex", alignItems: "center", gap: "10px" }}>
                            <span style={{ color: 'var(--primary-color)' }}>✦</span> Recommended Styles
                        </h3>
                        {occasions.length > 1 && (
                            <div className="chip-row" style={{ overflowX: "auto", paddingBottom: "4px" }}>
                                {occasions.map((occ) => (
                                    <button
                                        key={occ}
                                        className={`chip ${activeOccasion === occ ? "active" : ""}`}
                                        onClick={() => setActiveOccasion(occ)}
                                        style={activeOccasion !== occ && OCCASION_COLOR[occ] ? { "--chip-hover": OCCASION_COLOR[occ] } : {}}
                                    >
                                        {occ}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {filteredRecs.length === 0 ? (
                        <p style={{ color: "var(--text-dim)" }}>No items for this occasion. Try "All".</p>
                    ) : (
                        <div className="product-grid" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))" }}>
                            {filteredRecs.map((item, index) => {
                                const isProcessing = activeTryOn?.item?.item === item.item && activeTryOn.loading;
                                const isCurrentlyOnStage = activeTryOn?.item?.item === item.item && !activeTryOn.loading;

                                return (
                                    <Tilt
                                        key={index}
                                        className="product-card item-slide-in"
                                        style={{ animationDelay: `${index * 0.05}s` }}
                                        glareEnable={true}
                                        glareMaxOpacity={0.15}
                                        glarePosition="all"
                                        tiltMaxAngleX={4}
                                        tiltMaxAngleY={4}
                                        scale={1.02}
                                        transitionSpeed={1500}
                                    >
                                        <ProductImage src={item.image} alt={item.item} />
                                        <div className="product-info">
                                            {item.occasion && (
                                                <span className="occasion-tag">{item.occasion}</span>
                                            )}
                                            <h4>{item.item}</h4>
                                            <div className="shop-btns" style={{ marginBottom: "8px" }}>
                                                <button
                                                    className="shop-btn"
                                                    style={{
                                                        background: isCurrentlyOnStage ? 'transparent' : 'var(--accent-gradient)',
                                                        color: isCurrentlyOnStage ? 'var(--primary-color)' : 'white',
                                                        border: isCurrentlyOnStage ? '2px solid var(--primary-color)' : 'none',
                                                        cursor: isProcessing ? 'wait' : 'pointer',
                                                        width: '100%',
                                                        opacity: isProcessing ? 0.7 : 1,
                                                        fontWeight: isCurrentlyOnStage ? 'bold' : 'normal'
                                                    }}
                                                    onClick={() => handleTryOn(item)}
                                                    disabled={isProcessing}
                                                >
                                                    {isProcessing ? "✨ Loading Room..." : isCurrentlyOnStage ? "👕 In Fitting Room" : "👕 Try It On"}
                                                </button>
                                            </div>
                                            <div className="shop-btns">
                                                <a href={item.amazon} target="_blank" rel="noopener noreferrer" className="shop-btn amazon">🛒 Amazon</a>
                                                <a href={item.flipkart} target="_blank" rel="noopener noreferrer" className="shop-btn flipkart">🛍 Flipkart</a>
                                            </div>
                                        </div>
                                    </Tilt>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* RIGHT SIDE: STICKY VIRTUAL STAGE */}
                <div className="vfr-right" id="vfr-stage" style={{ maxHeight: "calc(100vh - 40px)", overflowY: "auto", paddingBottom: "20px" }}>
                    <Tilt
                        className="stage-card fade-in premium-stage"
                        style={{ animationDelay: "0.2s" }}
                        glareEnable={true}
                        glareMaxOpacity={0.08}
                        glarePosition="all"
                        tiltMaxAngleX={2}
                        tiltMaxAngleY={2}
                        scale={1.01}
                        transitionSpeed={2500}
                    >
                        <div className="stage-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                            <span>✨ Virtual Fitting Room</span>
                            {/* TINY ORIGINAL THUMBNAIL */}
                            {previewUrl && (
                                <div className="original-thumbnail" title="Your Original Photo" style={{ border: "2px solid rgba(255,255,255,0.2)", borderRadius: "8px", overflow: "hidden", width: "60px", height: "80px", flexShrink: 0, background: "#000" }}>
                                    <img src={previewUrl} alt="Original" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                                </div>
                            )}
                        </div>

                        {!activeTryOn ? (
                            <div className="tryon-placeholder">
                                <span className="icon">👕</span>
                                <p><strong>Select a garment!</strong><br />Click "Try It On" on any recommended item to see how it looks on you.</p>
                            </div>
                        ) : activeTryOn.loading ? (
                            <div className="tryon-placeholder ai-scanner-overlay" style={{ border: "2px solid var(--primary-color)" }}>
                                <div className="spinner-ring" style={{ width: "40px", height: "40px", borderTopColor: "var(--primary-color)" }}></div>
                                <p style={{ color: "var(--primary-color)", marginTop: "1rem", fontWeight: "bold" }}>AI is tailoring your outfit...</p>
                                <p style={{ fontSize: "0.85rem", opacity: 0.8 }}>This takes 15-30 seconds.</p>
                            </div>
                        ) : activeTryOn.image ? (
                            <div className="fade-in">
                                <img src={activeTryOn.image} alt="Try On Result" style={{ width: "100%", borderRadius: "12px", display: "block", border: "1px solid rgba(255,255,255,0.1)" }} />
                                <div style={{ marginTop: "1rem", textAlign: "center" }}>
                                    <p style={{ margin: "0 0 0.5rem 0", fontWeight: "bold", color: "var(--text-light)" }}>Now wearing: {activeTryOn.item.item}</p>
                                    <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--text-dim)" }}>This is an AI-generated preview.</p>
                                </div>
                            </div>
                        ) : (
                            <div className="tryon-placeholder">
                                <span className="icon">⚠️</span>
                                <p>Failed to load image. Please try another garment.</p>
                            </div>
                        )}
                    </Tilt>
                </div>
            </div>

            {/* ── COMPLETE THE LOOK (Outfit Builder) ── */}
            {outfits.length > 0 && (
                <div className="outfit-section">
                    <h3>✨ Complete the Look</h3>
                    <p style={{ color: "var(--text-dim)", marginTop: "-0.8rem", marginBottom: "1.5rem", fontSize: "0.92rem" }}>
                        Curated head-to-toe outfit combos for your body type
                    </p>
                    <div className="outfit-grid">
                        {outfits.map((outfit, idx) => (
                            <div key={idx} className="outfit-card">
                                <div className="outfit-card-body">
                                    <p className="outfit-label">Outfit {idx + 1}</p>
                                    <p className="outfit-name">{outfit.name}</p>
                                    <ul className="outfit-items-list">
                                        {outfit.items.map((piece, i) => (
                                            <li key={i}>{piece}</li>
                                        ))}
                                    </ul>
                                </div>
                                <a href={outfit.searchLink} target="_blank" rel="noopener noreferrer" className="outfit-shop-btn">
                                    🛒 Shop This Look
                                </a>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default ResultCard;
