/* SVG Silhouette helper for BodyTypeCard */
const SHAPES = {
    ectomorph: (
        <svg width="60" height="90" viewBox="0 0 60 90" fill="none">
            {/* Head */}
            <ellipse cx="30" cy="10" rx="9" ry="10" fill="currentColor" opacity="0.75" />
            {/* Body — narrow frame */}
            <rect x="20" y="22" width="20" height="32" rx="6" fill="currentColor" opacity="0.6" />
            {/* Legs — long & slim */}
            <rect x="20" y="55" width="8" height="33" rx="4" fill="currentColor" opacity="0.55" />
            <rect x="32" y="55" width="8" height="33" rx="4" fill="currentColor" opacity="0.55" />
            {/* Arms */}
            <rect x="8" y="22" width="10" height="26" rx="4" fill="currentColor" opacity="0.45" />
            <rect x="42" y="22" width="10" height="26" rx="4" fill="currentColor" opacity="0.45" />
        </svg>
    ),
    mesomorph: (
        <svg width="60" height="90" viewBox="0 0 60 90" fill="none">
            {/* Head */}
            <ellipse cx="30" cy="10" rx="10" ry="10" fill="currentColor" opacity="0.75" />
            {/* Broad shoulders / V torso */}
            <path d="M10 24 L50 24 L42 56 L18 56 Z" fill="currentColor" opacity="0.6" rx="4" />
            {/* Legs */}
            <rect x="18" y="56" width="10" height="32" rx="4" fill="currentColor" opacity="0.55" />
            <rect x="32" y="56" width="10" height="32" rx="4" fill="currentColor" opacity="0.55" />
            {/* Arms — muscular */}
            <rect x="2" y="24" width="10" height="28" rx="4" fill="currentColor" opacity="0.45" />
            <rect x="48" y="24" width="10" height="28" rx="4" fill="currentColor" opacity="0.45" />
        </svg>
    ),
    endomorph: (
        <svg width="60" height="90" viewBox="0 0 60 90" fill="none">
            {/* Head */}
            <ellipse cx="30" cy="10" rx="11" ry="10" fill="currentColor" opacity="0.75" />
            {/* Round body */}
            <ellipse cx="30" cy="42" rx="18" ry="18" fill="currentColor" opacity="0.6" />
            {/* Legs — shorter, wider */}
            <rect x="17" y="57" width="11" height="31" rx="5" fill="currentColor" opacity="0.55" />
            <rect x="32" y="57" width="11" height="31" rx="5" fill="currentColor" opacity="0.55" />
            {/* Arms */}
            <rect x="4" y="26" width="11" height="26" rx="5" fill="currentColor" opacity="0.45" />
            <rect x="45" y="26" width="11" height="26" rx="5" fill="currentColor" opacity="0.45" />
        </svg>
    ),
};

const INFO = {
    ectomorph: {
        tag: "Lean & Slender",
        color: "#74b9ff",
        traits: ["Narrow frame & small joints", "Fast metabolism", "Hard to gain weight"],
        dos: ["Add volume with layers", "Horizontal stripes", "Textured fabrics"],
        donts: ["Oversized fits", "Vertical stripes", "Baggy trousers"],
    },
    mesomorph: {
        tag: "Athletic & Muscular",
        color: "#55efc4",
        traits: ["Broad shoulders", "Well-defined V-torso", "Gains muscle easily"],
        dos: ["Fitted cuts", "V-necks", "Tailored suits"],
        donts: ["Boxy tops", "Padded shoulders", "Overly tight fits"],
    },
    endomorph: {
        tag: "Soft & Full",
        color: "#a29bfe",
        traits: ["Wider hips & midsection", "Stocky build", "Slower metabolism"],
        dos: ["Dark solid colours", "Structured blazers", "Vertical stripes"],
        donts: ["Horizontal stripes", "Baggy knitwear", "Light-colour bottoms"],
    },
};

export default function BodyTypeCard({ activeType }) {
    return (
        <div className="body-type-cards-row">
            {["ectomorph", "mesomorph", "endomorph"].map((type) => {
                const info = INFO[type];
                const isActive = type === activeType;
                return (
                    <div
                        key={type}
                        className={`body-type-card${isActive ? " active-type" : ""}`}
                        style={{ color: isActive ? info.color : "var(--text-dim)" }}
                        title={info.traits.join(" · ")}
                    >
                        {SHAPES[type]}
                        <p className="bt-name" style={{ color: isActive ? info.color : "var(--text-light)" }}>
                            {type}
                        </p>
                        <p className="bt-tag">{info.tag}</p>
                        {isActive && (
                            <div style={{ marginTop: "0.8rem", textAlign: "left" }}>
                                <p style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.8px", color: info.color, fontWeight: 700, marginBottom: "4px" }}>Do's</p>
                                {info.dos.map((d, i) => (
                                    <p key={i} style={{ fontSize: "0.75rem", color: "var(--text-dim)", margin: "2px 0" }}>✓ {d}</p>
                                ))}
                                <p style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.8px", color: "#e17055", fontWeight: 700, margin: "8px 0 4px" }}>Don'ts</p>
                                {info.donts.map((d, i) => (
                                    <p key={i} style={{ fontSize: "0.75rem", color: "var(--text-dim)", margin: "2px 0" }}>✗ {d}</p>
                                ))}
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
