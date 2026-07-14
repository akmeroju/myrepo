// Framer Code Component — Hero Section
// Drop this into Framer via Assets → Code → New Component → paste contents
// Then add it to your canvas as a full-viewport frame.

import { addPropertyControls, ControlType } from "framer"
import { motion, useReducedMotion } from "framer-motion"
import { useState, useEffect, useRef } from "react"

const GOLD = "#c9a84c"
const DARK = "#0a0a0a"
const BG = "#f5f4f2"
const TEXT = "#0a0a0a"
const BORDER = "rgba(0,0,0,0.08)"

// ── Types ────────────────────────────────────────────────────────────────────

interface Props {
    greeting: string
    firstName: string
    lastName: string
    role: string
    photo: string
    ctaLabel: string
    ctaHref: string
    resumeHref: string
    navLinks: string[]
    onScrollClick?: () => void
}

// ── Scroll hint ──────────────────────────────────────────────────────────────

function ScrollHint({ onClick }: { onClick?: () => void }) {
    const reduce = useReducedMotion()

    return (
        <motion.div
            onClick={onClick}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.1, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
                gap: 12,
                marginTop: 36,
                cursor: "pointer",
            }}
        >
            <span
                style={{
                    fontSize: "0.6rem",
                    fontWeight: 700,
                    letterSpacing: "0.3em",
                    textTransform: "uppercase",
                    color: GOLD,
                    fontFamily: "Poppins, sans-serif",
                }}
            >
                Scroll to explore
            </span>

            <div style={{ position: "relative", width: 52, height: 52 }}>
                {/* outer pulse ring */}
                <motion.div
                    animate={reduce ? {} : { scale: [1, 1.1, 1], opacity: [1, 0.4, 1] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.3 }}
                    style={{
                        position: "absolute",
                        inset: -16,
                        borderRadius: "50%",
                        border: `1px solid rgba(201,168,76,0.15)`,
                    }}
                />
                {/* inner pulse ring */}
                <motion.div
                    animate={reduce ? {} : { scale: [1, 1.1, 1], opacity: [1, 0.4, 1] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    style={{
                        position: "absolute",
                        inset: -8,
                        borderRadius: "50%",
                        border: `1px solid rgba(201,168,76,0.3)`,
                    }}
                />
                {/* arrow button */}
                <motion.div
                    animate={reduce ? {} : { y: [0, 8, 0] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    style={{
                        position: "relative",
                        width: 52,
                        height: 52,
                        borderRadius: "50%",
                        background: DARK,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        zIndex: 1,
                    }}
                >
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#fff"
                        strokeWidth={2}
                        style={{ width: 18, height: 18 }}
                    >
                        <path d="M12 5v14M5 15l7 7 7-7" />
                    </svg>
                </motion.div>
            </div>
        </motion.div>
    )
}

// ── Nav ──────────────────────────────────────────────────────────────────────

function Nav({
    navLinks,
    ctaLabel,
    ctaHref,
    resumeHref,
}: {
    navLinks: string[]
    ctaLabel: string
    ctaHref: string
    resumeHref: string
}) {
    const [scrolled, setScrolled] = useState(false)

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 20)
        window.addEventListener("scroll", onScroll, { passive: true })
        return () => window.removeEventListener("scroll", onScroll)
    }, [])

    return (
        <nav
            style={{
                position: "fixed",
                top: 0,
                left: 0,
                right: 0,
                height: 64,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "0 40px",
                zIndex: 100,
                background: scrolled ? "rgba(245,244,242,0.92)" : "transparent",
                backdropFilter: scrolled ? "blur(12px)" : "none",
                borderBottom: scrolled ? `1px solid ${BORDER}` : "none",
                transition: "background 0.3s, backdrop-filter 0.3s, border-bottom 0.3s",
                fontFamily: "Poppins, sans-serif",
            }}
        >
            {/* Logo */}
            <a
                href="#"
                style={{
                    fontSize: "1.05rem",
                    fontWeight: 800,
                    letterSpacing: "0.04em",
                    color: TEXT,
                    textDecoration: "none",
                }}
            >
                AKM
            </a>

            {/* Nav links */}
            <ul
                style={{
                    display: "flex",
                    gap: 36,
                    listStyle: "none",
                    margin: 0,
                    padding: 0,
                }}
            >
                {navLinks.map((link) => (
                    <li key={link}>
                        <a
                            href={`#${link.toLowerCase()}`}
                            style={{
                                fontSize: "0.68rem",
                                fontWeight: 600,
                                letterSpacing: "0.1em",
                                color: TEXT,
                                textDecoration: "none",
                                opacity: 0.55,
                                transition: "opacity 0.2s",
                            }}
                            onMouseEnter={(e) =>
                                (e.currentTarget.style.opacity = "1")
                            }
                            onMouseLeave={(e) =>
                                (e.currentTarget.style.opacity = "0.55")
                            }
                        >
                            {link.toUpperCase()}
                        </a>
                    </li>
                ))}
            </ul>

            {/* Right CTAs */}
            <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
                <a
                    href={resumeHref}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 6,
                        fontSize: "0.72rem",
                        fontWeight: 600,
                        letterSpacing: "0.06em",
                        color: TEXT,
                        textDecoration: "none",
                        opacity: 0.6,
                        transition: "opacity 0.2s",
                        fontFamily: "Poppins, sans-serif",
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.opacity = "1")}
                    onMouseLeave={(e) => (e.currentTarget.style.opacity = "0.6")}
                >
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={2}
                        style={{ width: 13, height: 13 }}
                    >
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                    </svg>
                    Resume
                </a>

                <a
                    href={ctaHref}
                    style={{
                        padding: "9px 22px",
                        background: DARK,
                        color: "#fff",
                        fontSize: "0.72rem",
                        fontWeight: 700,
                        letterSpacing: "0.1em",
                        textTransform: "uppercase",
                        textDecoration: "none",
                        transition: "background 0.2s",
                        fontFamily: "Poppins, sans-serif",
                    }}
                    onMouseEnter={(e) =>
                        (e.currentTarget.style.background = GOLD)
                    }
                    onMouseLeave={(e) =>
                        (e.currentTarget.style.background = DARK)
                    }
                >
                    {ctaLabel}
                </a>
            </div>
        </nav>
    )
}

// ── Main Component ───────────────────────────────────────────────────────────

export default function HeroSection({
    greeting,
    firstName,
    lastName,
    role,
    photo,
    ctaLabel,
    ctaHref,
    resumeHref,
    navLinks,
    onScrollClick,
}: Props) {
    return (
        <div
            style={{
                position: "relative",
                width: "100%",
                height: "100vh",
                background: BG,
                overflow: "hidden",
                fontFamily: "Poppins, sans-serif",
            }}
        >
            <Nav
                navLinks={navLinks}
                ctaLabel={ctaLabel}
                ctaHref={ctaHref}
                resumeHref={resumeHref}
            />

            {/* ── Photo (left 55%) ── */}
            <div
                style={{
                    position: "absolute",
                    top: 64,
                    left: 0,
                    width: "55%",
                    height: "calc(100vh - 64px)",
                    overflow: "hidden",
                }}
            >
                {photo ? (
                    <img
                        src={photo}
                        alt="Portrait"
                        style={{
                            width: "100%",
                            height: "100%",
                            objectFit: "cover",
                            objectPosition: "top center",
                            display: "block",
                        }}
                    />
                ) : (
                    // Placeholder when no photo is set
                    <div
                        style={{
                            width: "100%",
                            height: "100%",
                            background: "linear-gradient(160deg, #e8e4de, #d0cac2)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "rgba(0,0,0,0.25)",
                            fontSize: "0.8rem",
                            letterSpacing: "0.1em",
                            fontWeight: 600,
                        }}
                    >
                        PHOTO
                    </div>
                )}

                {/* Bottom fade gradient */}
                <div
                    style={{
                        position: "absolute",
                        bottom: 0,
                        left: 0,
                        width: "100%",
                        height: "28%",
                        background:
                            "linear-gradient(to top, rgba(245,244,242,0.7) 0%, rgba(245,244,242,0.25) 60%, transparent 100%)",
                        pointerEvents: "none",
                    }}
                />
            </div>

            {/* ── Vertical divider ── */}
            <div
                style={{
                    position: "absolute",
                    top: 64,
                    left: "55%",
                    width: 1,
                    height: "calc(100vh - 64px)",
                    background:
                        "linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.1) 20%, rgba(0,0,0,0.1) 80%, transparent 100%)",
                    zIndex: 8,
                    pointerEvents: "none",
                }}
            />

            {/* ── Text panel (right 45%) ── */}
            <div
                style={{
                    position: "absolute",
                    top: 64,
                    right: 0,
                    width: "45%",
                    height: "calc(100vh - 64px)",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    justifyContent: "center",
                    padding: "0 64px 0 52px",
                    zIndex: 10,
                }}
            >
                {/* Greeting */}
                <motion.p
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                    style={{
                        fontSize: "0.68rem",
                        fontWeight: 700,
                        letterSpacing: "0.2em",
                        textTransform: "uppercase",
                        color: "rgba(10,10,10,0.45)",
                        marginBottom: 10,
                        margin: 0,
                    }}
                >
                    {greeting}
                </motion.p>

                {/* Name */}
                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.35, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
                    style={{
                        fontSize: "clamp(2.6rem, 5.5vw, 6rem)",
                        fontWeight: 900,
                        lineHeight: 0.92,
                        color: TEXT,
                        letterSpacing: "-0.03em",
                        margin: "10px 0 0",
                        WebkitTextStroke: `1.5px ${GOLD}`,
                        paintOrder: "stroke fill",
                    }}
                >
                    {firstName}
                    <br />
                    {lastName}
                </motion.h1>

                {/* Role */}
                <motion.p
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                    style={{
                        fontSize: "0.85rem",
                        fontWeight: 400,
                        color: "rgba(10,10,10,0.55)",
                        marginTop: 18,
                        letterSpacing: "0.01em",
                    }}
                >
                    {role}
                </motion.p>

                {/* Scroll hint */}
                <ScrollHint onClick={onScrollClick} />
            </div>
        </div>
    )
}

// ── Property Controls ────────────────────────────────────────────────────────

addPropertyControls(HeroSection, {
    greeting: {
        type: ControlType.String,
        title: "Greeting",
        defaultValue: "Hello, I'm",
    },
    firstName: {
        type: ControlType.String,
        title: "First Name",
        defaultValue: "Adithya\nKumar",
    },
    lastName: {
        type: ControlType.String,
        title: "Last Name",
        defaultValue: "Meroju",
    },
    role: {
        type: ControlType.String,
        title: "Role",
        defaultValue: "Product Designer II  ·  Bengaluru, India",
    },
    photo: {
        type: ControlType.Image,
        title: "Photo",
    },
    ctaLabel: {
        type: ControlType.String,
        title: "CTA Label",
        defaultValue: "Hire Me",
    },
    ctaHref: {
        type: ControlType.String,
        title: "CTA Link",
        defaultValue: "#contact",
    },
    resumeHref: {
        type: ControlType.String,
        title: "Resume URL",
        defaultValue: "#",
    },
    navLinks: {
        type: ControlType.Array,
        title: "Nav Links",
        control: { type: ControlType.String },
        defaultValue: ["About", "Experience", "Work", "Skills", "Contact"],
    },
})
