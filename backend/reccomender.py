import urllib.parse

def get_recommendations(body_type):
    base_amazon   = "https://www.amazon.in/s?k="
    base_flipkart = "https://www.flipkart.com/search?q="

    # ── IMAGE BANK ────────────────────────────────────────────────────────────
    # All URLs are REAL Amazon product CDN images (m.media-amazon.com)
    # scraped live from amazon.in search results — guaranteed clothing product shots.
    # Format: cleaned to ._AC_UL500_.jpg for decent resolution.

    def amz(img_id):
        return f"https://m.media-amazon.com/images/I/{img_id}._AC_UL500_.jpg"

    # ECTOMORPH — 10 unique Amazon product images
    E = {
        "stripe_tee":    amz("51Kf8KjtkQL"),   # men stripe/multi-pack tee
        "bomber":        amz("71iUfYDCiGL"),   # men bomber jacket
        "slim_jeans":    amz("31UHY4yPdyL"),   # men slim fit blue jeans
        "knit_sweater":  amz("31nTkIlsDpL"),   # men knit sweater beige
        "denim_jacket":  amz("61E-m++RU1L"),   # men denim/casual jacket
        "dress_shirt":   amz("61GtS6IrR7L"),   # men formal dress shirt
        "flat_trousers": amz("61ZSIHDgCUL"),   # men flat-front formal trousers
        "pad_blazer":    amz("61cr6liBkVL"),   # men structured blazer
        "wool_suit":     amz("51JwxrGNdyL"),   # men formal two-piece suit
        "overshirt":     amz("61ii3hZB8fL"),   # men casual overshirt/layered
    }

    # MESOMORPH — 9 unique Amazon product images (zero overlap with ecto)
    M = {
        "fitted_tee":    amz("411cZXcsbAL"),   # men fitted gym/active tee
        "polo":          amz("81+PwGS-KrL"),   # men polo shirt
        "slim_shirt":    amz("31lqmZkK9qL"),   # men slim-fit casual shirt
        "leather_jkt":   amz("61j2FBMg2LL"),   # men leather biker jacket
        "henley":        amz("71J-Q7ATTBL"),   # men henley long sleeve
        "office_shirt":  amz("71jF3jICgqL"),   # men slim-fit office dress shirt
        "tailor_trou":   amz("7145k5HDcBL"),   # men tailored formal trousers
        "tailor_blaz":   amz("612cHibjR4L"),   # men tailored dark blazer
        "slim_suit":      amz("51oBu+DfOtL"),   # men party/slim blazer suit
    }

    # ENDOMORPH — 9 unique Amazon product images (zero overlap with above)
    N = {
        "vert_stripe":   amz("61+kpt5Q6sL"),   # men vertical stripe shirt
        "dark_tee":      amz("61uqWB-ccBL"),   # men dark navy solid t-shirt
        "dark_jeans":    amz("41r3Yu+ZnOL"),   # men straight-fit dark jeans
        "relaxed_chin":  amz("71d6Hkh-WJL"),   # men khaki chino relaxed
        "comfort_shirt": amz("61aZMa-pTrL"),   # men comfort-fit dark shirt
        "straight_trou": amz("61iGZG6zHuL"),   # men charcoal straight trousers
        "sb_blazer":     amz("81fc0BTNnQL"),   # men dark navy formal blazer
        "sb_suit":       amz("31bnVYIiHcL"),   # men dark single-breasted suit
        "party_blaz":    amz("716HXi-C6UL"),   # men structured party blazer
    }

    # ── HELPERS ───────────────────────────────────────────────────────────────
    def make_items(entries):
        return [{
            "item": name, "image": img, "occasion": occ,
            "amazon":   f"{base_amazon}{urllib.parse.quote(name + ' for men')}",
            "flipkart": f"{base_flipkart}{urllib.parse.quote(name + ' for men')}",
        } for name, img, occ in entries]

    def make_outfit(name, pieces, occ="Casual"):
        q = urllib.parse.quote(f"{name} outfit for men")
        return {"name": name, "occasion": occ, "items": pieces,
                "searchLink": f"{base_amazon}{q}"}

    # ── DATA ──────────────────────────────────────────────────────────────────
    data = {
        "ectomorph": {
            "description": [
                "Lean & slender frame — add visual volume and structure.",
                "Boxy/regular fits, horizontal stripes, and layered looks work best.",
                "Bomber jackets, textured fabrics, and padded blazers are ideal.",
            ],
            "items": [
                ("Horizontal Stripe Tee",    E["stripe_tee"],    "Casual"),
                ("Bomber Jacket",            E["bomber"],        "Casual"),
                ("Slim-Fit Jeans",           E["slim_jeans"],    "Casual"),
                ("Textured Knit Sweater",    E["knit_sweater"],  "Casual"),
                ("Denim Jacket",             E["denim_jacket"],  "Casual"),
                ("Regular-Fit Dress Shirt",  E["dress_shirt"],   "Office"),
                ("Flat-Front Trousers",      E["flat_trousers"], "Office"),
                ("Padded Shoulder Blazer",   E["pad_blazer"],    "Office"),
                ("Structured Wool Suit",     E["wool_suit"],     "Formal"),
                ("Layered Overshirt",        E["overshirt"],     "Party"),
            ],
            "outfits": [
                make_outfit("Casual Layered Look", [
                    "Horizontal Stripe Tee",
                    "Slim-Fit Jeans (mid blue)",
                    "Bomber / Denim Jacket",
                    "White Low-Top Sneakers",
                ], "Casual"),
                make_outfit("Office Sharp", [
                    "Regular-Fit Check Dress Shirt",
                    "Flat-Front Trousers (camel / grey)",
                    "Padded Shoulder Blazer",
                    "Brown Derby Shoes",
                ], "Office"),
                make_outfit("Formal Sharp", [
                    "Structured Wool Suit (charcoal)",
                    "White Dress Shirt + Medium-Width Tie",
                    "Oxford Cap-Toe Shoes",
                ], "Formal"),
            ],
        },

        "mesomorph": {
            "description": [
                "Athletic V-shaped build — highlight proportions, don't over-tighten.",
                "Slim-fit / tailored cuts, polo shirts, and tailored suits are ideal.",
                "Avoid overly tight clothes — they look forced on a muscular frame.",
            ],
            "items": [
                ("Fitted T-Shirt",           M["fitted_tee"],   "Casual"),
                ("Polo Shirt",               M["polo"],         "Casual"),
                ("Slim-Fit Casual Shirt",    M["slim_shirt"],   "Casual"),
                ("Leather Jacket",           M["leather_jkt"],  "Party"),
                ("Henley Shirt",             M["henley"],       "Party"),
                ("Tailored-Fit Dress Shirt", M["office_shirt"], "Office"),
                ("Tailored Trousers",        M["tailor_trou"],  "Office"),
                ("Tailored Blazer",          M["tailor_blaz"],  "Office"),
                ("Slim-Fit Suit",            M["slim_suit"],    "Formal"),
            ],
            "outfits": [
                make_outfit("Clean Casual", [
                    "Fitted T-Shirt (white or navy)",
                    "Tapered Chinos (beige)",
                    "Loafers or Clean Sneakers",
                ], "Casual"),
                make_outfit("Sharp Office", [
                    "Tailored-Fit Dress Shirt (light blue)",
                    "Tailored Trousers (navy)",
                    "Tailored Blazer + Derby Shoes",
                ], "Office"),
                make_outfit("Formal Statement", [
                    "Slim-Fit Suit (navy / charcoal)",
                    "White Dress Shirt + Cap-Toe Oxford Shoes",
                ], "Formal"),
            ],
        },

        "endomorph": {
            "description": [
                "Broader, fuller build — create a lean, elongated visual line.",
                "Dark solids, vertical stripes, and straight-fit cuts are your go-to.",
                "Avoid baggy (adds bulk) and skin-tight fits (highlights midsection).",
            ],
            "items": [
                ("Vertical Stripe Shirt",        N["vert_stripe"],   "Casual"),
                ("Dark Solid T-Shirt",           N["dark_tee"],      "Casual"),
                ("Straight-Fit Dark Jeans",      N["dark_jeans"],    "Casual"),
                ("Relaxed Chinos",               N["relaxed_chin"],  "Casual"),
                ("Comfort-Fit Dark Shirt",       N["comfort_shirt"], "Office"),
                ("Straight-Fit Trousers",        N["straight_trou"], "Office"),
                ("Single-Breasted Dark Blazer",  N["sb_blazer"],     "Office"),
                ("Single-Breasted Dark Suit",    N["sb_suit"],       "Formal"),
                ("Structured Dark Blazer",       N["party_blaz"],    "Party"),
            ],
            "outfits": [
                make_outfit("Weekend Casual", [
                    "Dark Solid T-Shirt (navy / charcoal)",
                    "Straight-Fit Dark Jeans",
                    "Clean White Sneakers",
                ], "Casual"),
                make_outfit("Office Streamlined", [
                    "Comfort-Fit Dark Shirt (navy)",
                    "Straight-Fit Trousers + Single-Breasted Dark Blazer",
                    "Derby Shoes",
                ], "Office"),
                make_outfit("Formal Elongated", [
                    "Single-Breasted Dark Suit (navy/charcoal, 2-button)",
                    "White Dress Shirt + Lightweight Oxford Shoes",
                ], "Formal"),
            ],
        },
    }

    result = data.get(body_type, {})
    if not result:
        return {}

    return {
        "description": result["description"],
        "recommendations": {
            "men":     make_items(result["items"]),
            "outfits": result["outfits"],
        },
    }
