# GitHub Issue Draft — gibwork-website Landing Page Improvements

> Prepared for the gib.work bounty ("detailed landing-page improvement proposal" option).
> **DRAFT — NOT PUBLISHED.** Влад: review before posting as an issue in `gibwork/gibwork-website`.

---

**Title:** Landing page audit — concrete UX, performance, SEO & accessibility improvements (with file references)

## Summary

I reviewed the `gibwork-website` codebase (Next.js 14 App Router + Tailwind + Radix/shadcn + Framer Motion). The page works, but there are a number of concrete, low-effort/high-impact fixes across SEO, Core Web Vitals, accessibility and conversion copy. Below is a prioritized list with exact file references.

## P0 — Performance (Core Web Vitals)

1. **Re-enable Next Image optimization.** `next.config.js` sets `images: { unoptimized: true }`. This disables all of Next's image pipeline site-wide. The hero screenshot (`dashboard-2.png`) ships at ~460 KB as an unoptimized PNG and is the LCP element.
   - Convert hero image to WebP/AVIF (~460 KB → ~60 KB), add `priority` and explicit `sizes`.
2. **Reduce client-side JS.** Nearly every section is `"use client"`, including static content (Footer, CTA, FAQ). Framer Motion is loaded for simple reveal animations that could be CSS-only. Moving static sections to server components would cut a meaningful amount of shipped JS.
3. **Trim duplicate dependencies:** Flowbite React is used for exactly one component (`Clipboard` in `components/hero.tsx`, which is dead code) while shadcn/Radix is already present; two icon libraries (`lucide-react` + `@tabler/icons-react`) are both installed. Consolidate to one.
4. **react-tweet runtime fetches:** the testimonial section embeds ~10 tweets, each fetched at runtime. Cache them (ISR/`revalidate`) or replace with static quote cards.

## P0 — SEO

5. **Metadata is minimal.** `app/layout.tsx` defines only title/description/og:image. Missing: `metadataBase`, canonical URLs, `twitter:card`, robots directives, per-page metadata (`/tokenomics` has none).
6. **No structured data.** Add JSON-LD for `Organization`, `WebSite`, and especially `FAQPage` — the FAQ content already exists in `components/faq.tsx` and is a prime rich-result candidate.
7. **Canonical host inconsistency.** `public/robots.txt` points to `www.gib.work` while the site config uses non-www `https://gib.work/`; sitemap should be generated dynamically (`app/sitemap.ts`) — current `public/sitemap.xml` has stale lastmod (2024‑08‑28) and lists only the homepage.
8. **OG image:** layout references a remote CDN URL while `public/og.png` sits unused locally.

## P1 — Accessibility

9. **Wrong/duplicate alt text:** all three card images in `components/looking-for.tsx` (~lines 105/120/135) share the same alt "Open Source Bounty" regardless of the actual card; the hero dashboard image uses empty alt (`hero.tsx:110`) but is meaningful and should describe the product.
10. **Mobile nav:** overlay menu (`nav.tsx:94–182`) lacks focus trap, Escape-to-close, `aria-expanded` on the toggle button, and body-scroll lock.
11. **Icon-only social buttons** have no `aria-label`s; no skip-to-content link exists.

## P1 — Conversion & copy

12. **Hero doesn't lead with the differentiator.** "Find Talent, Find Work" is generic; the crypto-native value prop (bounties paid in SOL/USDC, instant, non-custodial) is buried in FAQ comments. Lead with it.
13. **Single CTA repeated 4×**, all pointing externally to app.gib.work with `target="_blank"`. Add a secondary CTA ("View live bounties" / docs), and reconsider opening a new tab from the primary CTA.
14. **No quantitative social proof.** Hero/testimonials contain zero numbers. "X bounties paid · $Y USDC distributed" would materially improve trust.
15. **LogoList section contradicts itself:** heading says "Partners we have collaborated with", paragraph talks about the team. Split into two sections or rewrite the copy.

## P2 — Hygiene

16. Remove dead/commented code: token-CA block in `hero.tsx:80–104`, jup.ag link in `nav.tsx:43–45`, commented FAQ fee/token questions, unused Flowbite import.
17. Harden testimonials against deleted source tweets (hardcoded tweet IDs will silently break).
18. Add preconnect hints for `cdn.gib.work` / uploadthing, lazy-load below-fold embeds, run Lighthouse CI with perf budgets.

## Why this matters

These are mostly config/copy-level changes with no redesign required, but they directly affect Lighthouse scores, search visibility and conversion — the top of the funnel for bounty posters and hunters.

Happy to elaborate or PR any subset of these.
