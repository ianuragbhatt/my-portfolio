#!/usr/bin/env python3
"""
Blog build script — converts Markdown posts to HTML.

Usage:
    python build.py

Reads .md files from content/posts/, generates:
    - blog/posts/*.html  (individual articles)
    - blog/index.html    (listing page)
    - Updates index.html  (homepage blog preview)
"""

import os
import re
import yaml
import markdown
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content" / "posts"
BLOG_DIR = ROOT / "blog"
POSTS_DIR = BLOG_DIR / "posts"
INDEX_HTML = ROOT / "index.html"

# ─── Templates ───────────────────────────────────────────────

POST_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Anurag Bhatt</title>
    <link rel="stylesheet" href="../../css/style.css">
    <link rel="stylesheet" href="../../css/blog.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900&family=Fira+Code:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-content">
            <a href="../../" class="logo">AB.</a>
            <ul class="nav-links">
                <li><a href="../../#about">About</a></li>
                <li><a href="../../#experience">Experience</a></li>
                <li><a href="../../#projects">Work</a></li>
                <li><a href="../../blog/">Blog</a></li>
            </ul>
        </div>
    </nav>

    <main class="container">
        <div class="article-header">
            <a href="../../blog/" class="article-back"><i class="fas fa-arrow-left"></i> All Posts</a>
            <span class="article-category">{category}</span>
            <h1>{title}</h1>
            <div class="article-meta">
                <span><i class="far fa-calendar"></i> {date_display}</span>
                <span><i class="far fa-clock"></i> {read_time}</span>
            </div>
        </div>

        <hr class="article-divider">

        <article class="article-content">
            {content}
        </article>

        <div class="article-footer">
            <a href="../../blog/" class="article-back"><i class="fas fa-arrow-left"></i> All Posts</a>
        </div>

        <footer id="contact" class="site-footer">
            <div class="footer-content">
                <h2>Let's build<br>the future.</h2>
                <a href="mailto:anur4g.bhatt@outlook.com" class="btn primary-btn mt-6">Get in Touch</a>
                <div class="footer-links mt-12">
                    <a href="http://github.com/ianuragbhatt/" target="_blank" rel="noopener noreferrer"><i class="fab fa-github"></i> GitHub</a>
                    <a href="https://www.linkedin.com/in/ianuragbhatt/" target="_blank" rel="noopener noreferrer"><i class="fab fa-linkedin"></i> LinkedIn</a>
                    <a href="https://x.com/ianuragbhatt" target="_blank" rel="noopener noreferrer"><i class="fab fa-twitter"></i> Twitter</a>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 Anurag Bhatt. All rights reserved.</p>
                <p>Designed with intention.</p>
            </div>
        </footer>
    </main>

    <script src="../../js/script.js"></script>
</body>
</html>"""

BLOG_INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog | Anurag Bhatt</title>
    <link rel="stylesheet" href="../css/style.css">
    <link rel="stylesheet" href="../css/blog.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900&family=Fira+Code:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-content">
            <a href="../" class="logo">AB.</a>
            <ul class="nav-links">
                <li><a href="../#about">About</a></li>
                <li><a href="../#experience">Experience</a></li>
                <li><a href="../#projects">Work</a></li>
                <li><a href="./">Blog</a></li>
            </ul>
        </div>
    </nav>

    <main class="container">
        <div class="blog-hero">
            <h1>WRITING.</h1>
            <p>Thoughts on building production AI systems.</p>
        </div>

        <div class="blog-grid">
            {cards}
        </div>

        <footer id="contact" class="site-footer">
            <div class="footer-content">
                <h2>Let's build<br>the future.</h2>
                <a href="mailto:anur4g.bhatt@outlook.com" class="btn primary-btn mt-6">Get in Touch</a>
                <div class="footer-links mt-12">
                    <a href="http://github.com/ianuragbhatt/" target="_blank" rel="noopener noreferrer"><i class="fab fa-github"></i> GitHub</a>
                    <a href="https://www.linkedin.com/in/ianuragbhatt/" target="_blank" rel="noopener noreferrer"><i class="fab fa-linkedin"></i> LinkedIn</a>
                    <a href="https://x.com/ianuragbhatt" target="_blank" rel="noopener noreferrer"><i class="fab fa-twitter"></i> Twitter</a>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 Anurag Bhatt. All rights reserved.</p>
                <p>Designed with intention.</p>
            </div>
        </footer>
    </main>

    <script src="../js/script.js"></script>
</body>
</html>"""

BLOG_CARD = """\
            <a class="blog-card" href="{href}" data-animate>
                <span class="blog-card-category">{category}</span>
                <h3 class="blog-card-title">{title}</h3>
                <p class="blog-card-excerpt">{excerpt}</p>
                <div class="blog-card-meta">
                    <span><i class="far fa-calendar"></i> {date_display}</span>
                    <span><i class="far fa-clock"></i> {read_time}</span>
                </div>
            </a>"""


# ─── Helpers ─────────────────────────────────────────────────

def parse_post(filepath: Path) -> dict:
    """Read a Markdown file with YAML frontmatter."""
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.+?)\n---\n(.+)", text, re.DOTALL)
    if not match:
        raise ValueError(f"No valid frontmatter in {filepath}")

    meta = yaml.safe_load(match.group(1))
    body_md = match.group(2).strip()
    body_html = markdown.markdown(
        body_md,
        extensions=["fenced_code", "tables", "smarty"],
    )

    # Derive slug from filename
    slug = filepath.stem

    # Format date for display
    date_obj = meta["date"]
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
    meta["date_obj"] = date_obj
    meta["date_display"] = date_obj.strftime("%B %d, %Y")
    meta["slug"] = slug
    meta["content"] = body_html
    meta.setdefault("read_time", "5 min read")

    return meta


def build_post_html(post: dict) -> str:
    return POST_TEMPLATE.format(**post)


def build_card_html(post: dict, prefix: str = "posts/") -> str:
    return BLOG_CARD.format(
        href=f"{prefix}{post['slug']}.html",
        category=post["category"],
        title=post["title"],
        excerpt=post["excerpt"],
        date_display=post["date_display"],
        read_time=post["read_time"],
    )


def update_homepage_preview(posts: list[dict]):
    """Replace content between BLOG-PREVIEW markers in index.html."""
    html = INDEX_HTML.read_text(encoding="utf-8")

    start_marker = "<!-- BLOG-PREVIEW-START -->"
    end_marker = "<!-- BLOG-PREVIEW-END -->"

    if start_marker not in html:
        print("  [skip] No BLOG-PREVIEW markers found in index.html")
        return

    # Build preview cards (latest 2)
    preview_posts = posts[:2]
    cards = "\n".join(
        build_card_html(p, prefix="blog/posts/") for p in preview_posts
    )

    preview_html = f"""{start_marker}
            <div class="blog-preview-grid">
{cards}
            </div>
            <a href="blog/" class="view-all-link">View All Posts <i class="fas fa-arrow-right"></i></a>
            {end_marker}"""

    pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
    html = re.sub(pattern, preview_html, html, flags=re.DOTALL)
    INDEX_HTML.write_text(html, encoding="utf-8")
    print(f"  [updated] index.html preview ({len(preview_posts)} posts)")


# ─── Main ────────────────────────────────────────────────────

def main():
    # Ensure output dirs exist
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    # Collect and parse all posts
    md_files = sorted(CONTENT_DIR.glob("*.md"))
    if not md_files:
        print("No posts found in content/posts/")
        return

    posts = []
    for f in md_files:
        try:
            posts.append(parse_post(f))
        except Exception as e:
            print(f"  [error] {f.name}: {e}")

    # Sort by date, newest first
    posts.sort(key=lambda p: p["date_obj"], reverse=True)

    print(f"Building {len(posts)} post(s)...\n")

    # Generate individual post pages
    for post in posts:
        out_path = POSTS_DIR / f"{post['slug']}.html"
        out_path.write_text(build_post_html(post), encoding="utf-8")
        print(f"  [built] blog/posts/{post['slug']}.html")

    # Generate blog listing page
    cards = "\n".join(build_card_html(p) for p in posts)
    listing_html = BLOG_INDEX_TEMPLATE.format(cards=cards)
    (BLOG_DIR / "index.html").write_text(listing_html, encoding="utf-8")
    print(f"  [built] blog/index.html")

    # Update homepage preview
    update_homepage_preview(posts)

    print(f"\nDone. {len(posts)} post(s) published.")


if __name__ == "__main__":
    main()
