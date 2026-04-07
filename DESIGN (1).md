# Design System Specification: The Architectural Minimalist

This design system is a comprehensive framework crafted for high-end client management. It moves beyond "functional utility" into the realm of "digital hospitality." By treating the interface as a curated editorial space rather than a dense database, we instill confidence in high-value interactions.

## 1. Creative North Star: The Digital Curator
The guiding philosophy of this system is **The Digital Curator**. We aim to present complex client data through a lens of extreme clarity and intentionality. The design avoids the "boxed-in" feeling of traditional SaaS by utilizing expansive white space, asymmetric layouts, and tonal depth. We don't just show information; we stage it.

- **Intentional Asymmetry:** Avoid perfectly centered grids for every module. Use "Weighted Negative Space" where a narrow sidebar or a large header creates a sophisticated, off-balance look that feels designed, not templated.
- **Atmospheric Clarity:** The UI should feel like a high-end physical gallery—quiet, premium, and focused on the "art" (the client data).

## 2. Color & Tonal Architecture
The palette is rooted in a "Crisp White & Slate" foundation, punctuated by a deep, authoritative Royal Blue (`primary`).

### The "No-Line" Rule
**Explicit Instruction:** Traditional 1px solid borders are prohibited for sectioning. Structural boundaries must be defined solely through background color shifts or tonal transitions.
- **Example:** A `surface-container-low` (#f2f4f6) section sitting on a `surface` (#f7f9fb) background provides all the separation required without the visual "noise" of a line.

### Surface Hierarchy & Nesting
Treat the UI as layered sheets of premium paper. Use the Material tiers to create an "inner-to-outer" depth:
- **Base Layer:** `surface` (#f7f9fb) for the main application background.
- **Secondary Workspaces:** `surface-container-low` (#f2f4f6) for large side panels or secondary content areas.
- **Actionable Cards:** `surface-container-lowest` (#ffffff) to make interactive elements "pop" forward naturally.
- **Elevated Modals:** `surface-bright` (#f7f9fb) with high-diffusion shadows.

### The Glass & Gradient Rule
To achieve a signature feel, use **Glassmorphism** for floating headers or navigation overlays. 
- Use a semi-transparent `surface` color (e.g., `rgba(247, 249, 251, 0.8)`) with a `backdrop-blur: 20px`.
- **Signature Texture:** Primary CTAs should use a subtle linear gradient from `primary` (#00327d) to `primary_container` (#0047ab) at a 135-degree angle to add "soul" and dimension.

## 3. Typography: The Editorial Scale
We use a dual-font approach to balance authoritative headers with highly legible data.

- **Display & Headlines (Manrope):** Chosen for its geometric precision. Use `display-lg` to `headline-sm` for high-level summaries and client names. This provides the "Editorial" feel.
- **Body & Interface (Inter):** The workhorse. Use `body-md` (0.875rem) for the majority of client data to maintain a professional, compact density without sacrificing readability.
- **Hierarchy via Tonal Weight:** Instead of just changing size, use color tokens. Use `on_surface` (#191c1e) for primary headings and `on_secondary_container` (#57657a) for secondary metadata to create an effortless visual path for the eye.

## 4. Elevation & Depth
Depth is a tool for focus, not just decoration.

- **The Layering Principle:** Stack `surface-container` tiers. A `surface-container-lowest` card placed on a `surface-container-low` background creates a "soft lift" that feels architectural rather than digital.
- **Ambient Shadows:** When an element must float (e.g., a dropdown or modal), use an ultra-diffused shadow: `box-shadow: 0 12px 40px rgba(25, 28, 30, 0.06);`. The shadow color is a tinted version of `on-surface`, never pure black.
- **The "Ghost Border" Fallback:** If a border is required for accessibility in forms, use `outline-variant` (#c3c6d5) at 20% opacity. **Never use 100% opaque borders.**

## 5. Signature Components

### Buttons & CTAs
- **Primary:** Gradient-filled (`primary` to `primary_container`), `md` (0.75rem) rounded corners, generous horizontal padding (24px).
- **Tertiary:** No background or border. Use `primary` text weight with a subtle `primary_fixed` (#dae2ff) background shift on hover.

### Form Structures
- **The Floating Input:** Use `surface-container-lowest` for the input background. Upon focus, the `outline` (#737784) should transition to `primary` (#00327d) at 2px, but only on the bottom edge or as a very subtle 10% opacity glow.
- **Labels:** Use `label-md` in `on_surface_variant`. They should never "shout"; they guide.

### Cards & Lists
- **Forbid Divider Lines:** Separate list items using `12px` of vertical white space or a very subtle alternating background of `surface` and `surface-container-low`.
- **Client Profile Cards:** Use `xl` (1.5rem) rounded corners for the outer container and `md` (0.75rem) for inner elements to create a nested, professional look.

### Additional Premium Components
- **Status Indicator Pillars:** Instead of round dots, use thin vertical "pillars" (2px wide) on the left edge of a card using the `tertiary` (#651f00) or `primary` colors to denote status.
- **The Contextual Breadcrumb:** A large `headline-sm` title paired with a `label-sm` category tag above it, creating a "Museum Label" effect.

## 6. Do’s and Don’ts

### Do:
- **Do** use "Double Padding." If you think a container has enough padding, add 8px more. White space is our primary luxury signifier.
- **Do** use `inter` for all numerical data. Manrope's numbers are too "stylized" for financial or CRM data.
- **Do** use `surface-tint` (#2559bd) at 5% opacity for hover states on white cards to create a "cool" professional glow.

### Don’t:
- **Don’t** use pure black (#000000) for text. Always use `on_surface` (#191c1e).
- **Don’t** use standard "Select" dropdowns. Build custom "Pop-over" menus using the Glassmorphism rules.
- **Don’t** crowd the corners. Maintain a minimum "Safe Zone" of 32px from the edge of the browser window for all primary content.