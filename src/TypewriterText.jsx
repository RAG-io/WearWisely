import React, { useState, useEffect } from 'react';
import './App.css';

export default function TypewriterText({ text, speed = 120 }) {
    const [displayedText, setDisplayedText] = useState("");

    useEffect(() => {
        let i = 0;
        const interval = setInterval(() => {
            setDisplayedText(text.slice(0, i));
            i++;
            if (i > text.length) clearInterval(interval);
        }, speed);
        return () => clearInterval(interval);
    }, [text, speed]);

    return (
        <span>
            {displayedText}
            <span className="cursor-blink">_</span>
        </span>
    );
}
