import { useState } from "react";
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
function ResultCard({ result }) {
    const [activeOccasion, setActiveOccasion] = useState("All");

    if (!result) return null;

    const recs = result.recommendations?.men ?? [];
    const outfits = result.recommendations?.outfits ?? [];

    const occasions = ["All", ...Array.from(new Set(recs.map((r) => r.occasion).filter(Boolean)))];
    const filteredRecs = activeOccasion === "All"
        ? recs
        : recs.filter((r) => r.occasion === activeOccasion);

    const lowConf = result.confidence < 0.60;

    return (
        <div className="glass-card fade-in" style={{ maxWidth: "960px", margin: "40px auto", textAlign: "left" }}>

            {/* ── HEADER ── */}
            <div className="result-header">
                <h2 style={{ margin: 0, fontSize: "clamp(1.4rem, 3vw, 2rem)" }}>
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
                <h3 style={{ color: "var(--text-light)", marginBottom: "1rem" }}>Body Type Overview</h3>
                <BodyTypeCard activeType={result.body_type} />
                {result.description && (
                    <ul style={{ color: "var(--text-dim)", lineHeight: "1.7", fontSize: "0.95rem", paddingLeft: "1.2rem" }}>
                        {result.description.map((desc, i) => (
                            <li key={i} style={{ marginBottom: "6px" }}>{desc}</li>
                        ))}
                    </ul>
                )}
            </div>

            {/* ── OCCASION FILTER ── */}
            {occasions.length > 1 && (
                <div className="filter-section">
                    <p className="filter-label">Filter by Occasion</p>
                    <div className="chip-row">
                        {occasions.map((occ) => (
                            <button
                                key={occ}
                                className={`chip ${activeOccasion === occ ? "active" : ""}`}
                                onClick={() => setActiveOccasion(occ)}
                                style={activeOccasion !== occ && OCCASION_COLOR[occ]
                                    ? { "--chip-hover": OCCASION_COLOR[occ] }
                                    : {}}
                            >
                                {occ}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* ── PRODUCT GRID ── */}
            <div>
                <h3 style={{ color: "var(--text-light)", marginBottom: "1.2rem" }}>
                    Recommended Styles
                    {activeOccasion !== "All" && (
                        <span style={{ fontSize: "0.85rem", color: "var(--text-dim)", fontWeight: 400, marginLeft: "10px" }}>
                            — {activeOccasion}
                        </span>
                    )}
                </h3>
                {filteredRecs.length === 0 ? (
                    <p style={{ color: "var(--text-dim)" }}>No items for this occasion. Try "All".</p>
                ) : (
                    <div className="product-grid">
                        {filteredRecs.map((item, index) => (
                            <div key={index} className="product-card">
                                <ProductImage src={item.image} alt={item.item} />
                                <div className="product-info">
                                    {item.occasion && (
                                        <span className="occasion-tag">{item.occasion}</span>
                                    )}
                                    <h4>{item.item}</h4>
                                    <div className="shop-btns">
                                        <a href={item.amazon} target="_blank" rel="noopener noreferrer" className="shop-btn amazon">
                                            🛒 Amazon
                                        </a>
                                        <a href={item.flipkart} target="_blank" rel="noopener noreferrer" className="shop-btn flipkart">
                                            🛍 Flipkart
                                        </a>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
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
