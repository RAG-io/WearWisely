import { useState, useRef } from "react";
import axios from "axios";
import ResultCard from "./ResultCard";

const STATUS_STEPS = [
    "Uploading photo…",
    "Running AI model…",
    "Fetching recommendations…",
    "Almost there…",
];

function formatBytes(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function Upload() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [statusIdx, setStatusIdx] = useState(0);
    const [dragging, setDragging] = useState(false);
    const fileInputRef = useRef(null);
    const statusInterval = useRef(null);

    const applyFile = (selectedFile) => {
        if (!selectedFile || !selectedFile.type.startsWith("image/")) return;
        setFile(selectedFile);
        setPreview(URL.createObjectURL(selectedFile));
        setResult(null);
    };

    const handleFileChange = (e) => applyFile(e.target.files[0]);

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragging(true);
    };
    const handleDragLeave = () => setDragging(false);
    const handleDrop = (e) => {
        e.preventDefault();
        setDragging(false);
        applyFile(e.dataTransfer.files[0]);
    };

    const clearFile = (e) => {
        e.stopPropagation();
        setFile(null);
        setPreview(null);
        setResult(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    const handleUpload = async () => {
        if (!file) return;
        const formData = new FormData();
        formData.append("file", file);

        setLoading(true);
        setStatusIdx(0);
        let step = 0;
        statusInterval.current = setInterval(() => {
            step = Math.min(step + 1, STATUS_STEPS.length - 1);
            setStatusIdx(step);
        }, 900);

        try {
            const response = await axios.post("http://127.0.0.1:8000/predict", formData);
            setResult(response.data);
        } catch (error) {
            console.error(error);
            const msg = error.response?.data?.detail || "Error connecting to backend. Is the server running?";
            alert(msg);
        } finally {
            clearInterval(statusInterval.current);
            setLoading(false);
            setStatusIdx(0);
        }
    };

    return (
        <div>
            {/* ── DROP ZONE ── */}
            {!result && !loading && (
                <div
                    className={`dropzone advanced ${dragging ? "dragging" : ""}`}
                    style={{ maxWidth: "620px", margin: "0 auto" }}
                    onClick={() => !preview && fileInputRef.current.click()}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                >
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        style={{ display: "none" }}
                        accept="image/*"
                    />

                    {preview ? (
                        <div className="preview-wrapper">
                            <img src={preview} alt="Preview" />
                            <button className="preview-remove" onClick={clearFile} title="Remove image">✕</button>
                        </div>
                    ) : (
                        <div className="upload-placeholder">
                            <span className="upload-icon">📸</span>
                            <p className="upload-hint">
                                <strong>Drag & drop</strong> your photo here, or{" "}
                                <strong>click to browse</strong>
                            </p>
                            <p className="upload-sub">Full-body photo recommended · JPEG, PNG, WEBP</p>
                        </div>
                    )}
                </div>
            )}

            {/* File name + size */}
            {file && !loading && !result && (
                <p className="upload-file-info">
                    📎 {file.name} &nbsp;·&nbsp; {formatBytes(file.size)}
                </p>
            )}

            {/* ── LOADING STATE WITH AI SCANNER ── */}
            {loading && (
                <div className="loader-overlay" style={{ marginTop: "2rem" }}>
                    <div className="spinner-ring" />
                    <p className="loader-status" style={{ fontSize: "1.2rem", color: "var(--primary-color)" }}>{STATUS_STEPS[statusIdx]}</p>

                    {preview && (
                        <div className="ai-scanner-overlay" style={{ marginTop: "2rem", maxWidth: "400px", margin: "2rem auto", borderRadius: "16px", overflow: "hidden", border: "2px solid var(--primary-color)" }}>
                            <img src={preview} alt="Scanning" style={{ width: "100%", height: "auto", display: "block", filter: "brightness(0.7) contrast(1.1)" }} />
                        </div>
                    )}
                </div>
            )}

            {!loading && !result && (
                <div style={{ marginTop: "24px", textAlign: "center" }}>
                    <button
                        onClick={handleUpload}
                        className="btn-primary"
                        disabled={!file}
                        style={{ opacity: !file ? 0.45 : 1, minWidth: "200px" }}
                    >
                        ✨ Analyze My Style
                    </button>
                </div>
            )}

            {result && !loading && (
                <div className="fade-in">
                    <button onClick={clearFile} className="btn-secondary" style={{ marginBottom: "1rem" }}>
                        ← Start Over
                    </button>
                    <ResultCard result={result} userPhotoFile={file} previewUrl={preview} />
                </div>
            )}
        </div>
    );
}

export default Upload;
