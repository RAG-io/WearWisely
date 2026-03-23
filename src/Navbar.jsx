import { useState } from "react";
import { NavLink } from "react-router-dom";

export default function Navbar({ theme, toggleTheme }) {
    return (
        <nav className="navbar">
            <NavLink to="/" className="navbar-brand">
                WearWisely
            </NavLink>

            <div className="navbar-links">
                <NavLink to="/" end className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>
                    Home
                </NavLink>
                <NavLink to="/how-it-works" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>
                    How It Works
                </NavLink>
                <NavLink to="/about" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>
                    About
                </NavLink>

                <button className="theme-toggle" onClick={toggleTheme} title="Toggle theme">
                    {theme === "dark" ? "☀️ Light" : "🌙 Dark"}
                </button>
            </div>
        </nav>
    );
}
