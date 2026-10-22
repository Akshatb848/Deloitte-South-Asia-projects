"""Capture README screenshots of the running dashboard with headless Chromium.

Usage (backend on :8000, repo root served on :8080):
    python -m http.server 8080 &            # from the repository root
    python scripts/capture_screenshots.py http://localhost:8080/frontend/index.html docs/screenshots

Requires `pip install playwright && playwright install chromium`.
Set CHROMIUM_PATH to use an existing Chromium binary instead.
"""
import asyncio
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

QUESTION = "How many smart classrooms and computer labs were there?"


async def main(url: str, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        launch_args = {"args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if os.getenv("CHROMIUM_PATH"):
            launch_args["executable_path"] = os.environ["CHROMIUM_PATH"]
        browser = await p.chromium.launch(**launch_args)
        page = await browser.new_page(viewport={"width": 1440, "height": 1200})
        page.on("pageerror", lambda e: print("pageerror:", e))
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3500)  # let stat counters and charts animate
        await page.screenshot(path=str(out_dir / "dashboard.png"))
        await page.screenshot(path=str(out_dir / "dashboard-full.png"), full_page=True)

        await page.click("#chatbotToggle")
        await page.wait_for_timeout(600)
        await page.fill("#chatbotInput", QUESTION)
        await page.click("#chatbotSend")
        await page.wait_for_selector("#loadingMessage", state="detached", timeout=60000)
        await page.wait_for_timeout(800)
        # Scroll so the question and the start of the answer are both visible.
        await page.evaluate(
            "() => { const m = document.getElementById('chatbotMessages');"
            " const u = m.querySelectorAll('.message.user'); const t = u[u.length - 1];"
            " m.scrollTop = t.offsetTop - m.offsetTop - 12; }"
        )
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(out_dir / "chat-retrieval-only.png"))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], Path(sys.argv[2] if len(sys.argv) > 2 else "docs/screenshots")))
