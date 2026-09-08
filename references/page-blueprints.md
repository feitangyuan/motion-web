# Page Blueprints — 这个页面到底该有哪些板块，每块写什么

`page-design.md` §1 picks the **macrostructure** (single scene / acts / editorial / index / instrument).
This file is the layer under it: which named sections exist, in what order, and what each one owes in
actual words. It is the answer to "给我一个主题，我不知道这页要放什么".

**The rule:** sections come from what the visitor needs to decide, not from a template. But "not from a
template" does not mean "invent from nothing" — there is a real vocabulary, and knowing it is what lets
you deviate on purpose.

Measured from the same 32-site run as `components.md` §1:

| | Creative (n=18) | Product (n=14) |
|---|---|---|
| Sections above 0.15 vh | median **4.5** (0–14) | median **7** (1–24) |
| Distinct section *shapes* | median **2.5** | median **5** |
| Page height | median 8.3 vh, bimodal (1 vh or 7–49 vh) | median 10.1 vh |
| Full-bleed sections | 83 % | 32 % |
| Sections that switch background | 32 % | 14 % |

Two readings. **A creative page is short on sections and long on scroll** — few bands, each one big.
**A product page is the opposite** — more bands, each one screen-ish, mostly inset rather than
full-bleed. And the variety number is the one that matters: `design-slop.md` A3 demands ≥ 3 *different*
section shapes, and the creative median of 2.5 says a real page barely clears that bar. If your draft
has 8 sections and 2 shapes, it is a template regardless of how good the type is.

---

## §1 The section vocabulary

Every section below is a real, named thing. Use the name in the plan and in the file structure
(`sections/Manifesto.astro`), so "add a section" becomes a decision instead of a reflex.

**Openers**
| Section | It exists to | Owes |
|---|---|---|
| `Announcement` | say one time-bound thing (launch, deadline) | a dismiss, and a reason to exist — delete it otherwise |
| `Hero` | say what this is, for whom, in one screen | one `<h1>`, one verb, the LCP element |
| `Statement` / `Manifesto` | assert a position instead of describing a product | something arguable; a platitude here kills the page |

**Body — the part that actually varies**
| Section | It exists to | Owes |
|---|---|---|
| `Proof` (logos / press / numbers) | borrow credibility | **real** logos and numbers, or delete it (`design-slop.md` A8) |
| `Problem` | name the reader's situation before selling | the reader's words, not the product's |
| `Features` | list peer capabilities | ≥ 2 different shapes if used twice; never 3 equal centred cards |
| `Deep-dive` | show *one* thing properly | a real artifact — screenshot, video, live demo — not an icon |
| `How-it-works` / `Steps` | make a process legible | ordered markup, and a real number of steps (3–5) |
| `Work` / `Selected projects` | show, not claim | per-item: what it was, what you did, the outcome |
| `About` / `Approach` | say who is behind it | a specific fact; "we are passionate about design" is filler |
| `Story` / `Timeline` | give a sequence meaning | dates that are real |
| `Testimonial` | let someone else say it | attribution: name, role, source |
| `Pricing` | remove the last objection | every tier's actual limits, and what happens at the edge |
| `FAQ` | answer the objections you keep hearing | real questions; a fake FAQ is transparent |
| `Editorial passage` | just be read | measure ≤ 68ch, and a reason the reader stays |

**Closers**
| Section | It exists to | Owes |
|---|---|---|
| `CTA` | ask once, clearly | one action; two competing CTAs is zero CTAs |
| `Contact` | be reachable | a real address/form, and what happens after submit |
| `Footer` | catch everything else | see `components.md` §14 |

**Nothing on this list is mandatory except `Hero` (or its replacement) and `Footer`.** A campaign page
can be `Hero → Statement → CTA → Footer` and be finished.

---

## §2 Blueprints

Each blueprint gives a **spine** (the sections that carry the job) and the **shape mix** that keeps it
off the template. Shapes are drawn from: full-bleed / inset, 1-col / 2-col / grid, type-over-media /
type-beside-media, left / centred, light / dark ground.

### A · Product or service landing
```
Hero (type-beside-media, left, inset)
Proof (full-bleed rule of logos — only if real)
Problem (1-col, wide measure, ground switch)
Deep-dive ×2  (asymmetric: 60/40 then 40/60, one with a real screenshot)
How-it-works (numbered, full-bleed)
Testimonial (single large quote, ground switch)
Pricing (table or ≤3 cards)
FAQ (<details> list, narrow measure)
CTA (short, full-bleed)
Footer (multi-column)
```
7–10 sections, 4–6 shapes. **Where it goes wrong:** `Features` rendered three times as three equal
cards. Replace at least one with a deep-dive on a single capability.

### B · Portfolio / personal
```
Hero — usually the mechanic itself, name + one line of what you do
Selected work ×3–6 (index or staggered, each a real link)
About (1-col, narrow, one specific fact)
Capability list (typographic, not icons)
Contact (direct, no form if a mailto will do)
Footer (2 columns, small)
```
5–7 sections. **Where it goes wrong:** a skills bar chart, a "Tools I use" icon wall, and no actual
work. One properly-shown project beats six thumbnails.

### C · Studio / agency
```
Hero (statement, full-bleed, type over motion)
Work index (the real content — most of the page)
Services (typographic list, not cards)
Approach / Manifesto (editorial, ground switch)
Clients (real logos or nothing)
Contact + Footer
```
5–8 sections, and the work index should be ≥ 40 % of the page height. **Where it goes wrong:** the
manifesto is longer than the work.

### D · Campaign / launch / event  → usually `single scene` or `acts`
```
Act 1  the hook — what is happening
Act 2  the substance — one demonstrated idea
Act 3  the ask — date, place, price, button
Footer (minimal)
```
3–5 pinned beats, one money frame each (`timeline-orchestration.md`). Sections in the DOM sense may not
exist at all. **Where it goes wrong:** three acts that are all "here is a cool visual" with no ask.

### E · Editorial long-form
```
Title block (full-bleed, oversized type, deck ≤ 30 words)
Passage / Set-piece / Passage / Set-piece …   (2–4 set-pieces total)
Pull quotes and figures at the rhythm of the argument
Author / source note
Related or Footer
```
Motion punctuates; it does not narrate. Measure 60–75ch throughout. **Where it goes wrong:** a set-piece
every screen, which turns reading into scroll-jacking.

### F · Index / archive (work list, blog, gallery)
```
Header + filter (state in the URL)
The list — one row/card per item, dense, scannable
Empty state (designed)
Pagination or infinite scroll (with a real end)
Footer
```
The motion lives in transitions and hover, not in sections (`page-design.md` §1). **Where it goes
wrong:** the list is nine identical cards with no metadata to scan by — date, type, client, tag.

### G · Docs / reference (light)
```
Sidebar nav (current item marked) · Content (measure ≤ 75ch) · On-page TOC
Prev/next at the bottom
```
Motion budget here is near zero. If the brief is a real docs site, this skill is the wrong tool past the
landing page.

---

## §3 Ordering: what actually decides the sequence

Order is not taste. Three rules resolve most of it:

1. **Answer the question the previous section raised.** Hero says what it is → the reader asks "does it
   work?" → proof or deep-dive, not pricing. If a section answers nothing that came before, it is in the
   wrong place or should not exist.
2. **Objections descend.** The generic objection ("what is this?") is at the top, the specific one
   ("what if I need to cancel?") is at the bottom. Pricing and FAQ are late for this reason.
3. **The ask comes after the reason, and only once.** A CTA repeated in every section reads as anxiety.
   One in the nav (product dialect) and one at the end is the ceiling.

**Rhythm, not just order.** Vary the spacing between bands with intent — tight where two belong
together, `--section-loose` before a beat you want landed (`project-setup.md` §3). Even spacing produces
a list. And vary the *ground*: 32 % of creative sections switch background, which is what makes a long
page feel like it has chapters.

---

## §4 Copy is the design's other half

A section with placeholder copy has not been designed, because the layout is a response to real text
length. Write the words before or while laying out — never after.

**What each opener owes, concretely:**
- **`<h1>`**: what this *is*, ideally with a noun. "Freight scheduling that survives a bad day" beats
  "Reimagining logistics". If the headline works for any other company, it is not a headline.
- **The line under it**: who it is for, and the one thing it does. ≤ 25 words, ≤ 48ch measure.
- **The button label**: the verb the visitor is about to do — "Book a walkthrough", not "Learn more".
- **Section headings**: a claim, not a label. "Everything syncs offline" beats "Features".

**Rules that keep it honest:**
- **If the user did not supply a number, a logo, a quote or a client name, it does not go on the page.**
  Build the section with a visibly labelled placeholder (`[client logo]`) or choose a spine that does not
  need proof. Inventing it is `design-slop.md` A8 and it is the fastest way to lose trust in the whole
  deliverable.
- **Say the specific thing.** "Built for teams that ship on Fridays" tells you more than three paragraphs
  of "seamless, powerful, intuitive".
- **Chinese copy has its own rhythm** — short clauses, no comma splices imported from English syntax, and
  display lines that are 6–12 characters rather than 6–12 words. A translated English headline reads as
  translated. Set the Latin face separately in mixed lines (`page-design.md` §4).
- **Microcopy is content**: empty states, error messages, the line under the submit button, the 404. They
  are where the page's voice either exists or doesn't (`production-polish.md` §4).

**When the user gives you a topic and nothing else**: pick the blueprint, write the real copy yourself as
a first draft, and mark every factual slot you had to invent with `[…]`. Then say which slots need their
input. That is a deliverable; a page of lorem ipsum is not.

---

## §5 Information architecture: one page or several

| Signal | Answer |
|---|---|
| One offer, one audience, one decision | **one page**, anchors only |
| A body of work to browse | **index + detail routes** — each project deserves a URL |
| Content authored as files, and growing | **routes + a collection** (`project-setup.md` §1 rung 2) |
| Anything that must be linkable or shareable on its own | its own route, not a modal |

- **Nav links should map to sections or routes that exist.** A nav item that scrolls to a band with no
  heading is a dead link with extra steps.
- **Anchor IDs are a public API** — `#work`, not `#section-3`. Add `scroll-margin-block` so a fixed
  header doesn't cover the target (`project-setup.md` §5).
- **Past ~10 viewports the visitor needs a map**: progress indicator, changing section labels, or a
  persistent element that transforms (`page-design.md` §6). Native `scroll-target-group` scroll-spy is
  one line of CSS (`pattern-recipes.md` #16).

---

## §6 How this maps onto the motion macrostructure

| `page-design.md` §1 shape | Blueprint | Where the mechanic sits |
|---|---|---|
| Single scene | D | it *is* the page; DOM sections may not exist |
| Acts | D, E | one per act, sharing a vocabulary |
| Editorial + set-pieces | E, A | 2–4 punctuation points between passages |
| Index / archive | F, B, C | in transitions and hover, not inside a band |
| Single screen instrument | D | the entire page; scroll is not the verb |

**Pick the blueprint and the macrostructure together.** Forcing a browsable body of work (B/C/F) onto a
scroll rail is the most common structural mistake, and it surfaces later as "这一段什么都没发生"
(`timeline-orchestration.md` §1) — which is a *structure* bug being reported as a timing bug.

---

## §7 Checklist

- [ ] Blueprint named, and every section on the page is on the vocabulary list or deliberately invented (§1, §2)
- [ ] ≥ 3 distinct section shapes; no page where every band is centred headline + paragraph (§2, `design-slop.md` A3)
- [ ] Each section answers a question the previous one raised; nothing is there "because pages have one" (§3)
- [ ] Section spacing and ground varied with intent, not constant (§3)
- [ ] Real copy written, not placeholder; `<h1>` would not work for any other client (§4)
- [ ] Every invented fact marked `[…]` and reported to the user (§4)
- [ ] One-page vs multi-route decided from the content, not the effort (§5)
- [ ] Nav items map to real anchors/routes; anchor IDs are meaningful; `scroll-margin` set (§5)
- [ ] Blueprint and motion macrostructure chosen together and compatible (§6)
