import asyncio
import secrets
from contextlib import asynccontextmanager
from datetime import date, timedelta
from zoneinfo import ZoneInfo

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from wall_tidbits import builder, html, views
from wall_tidbits.cache import DailyCache
from wall_tidbits.config import Settings, load_settings
from wall_tidbits.dating import next_refresh_at, now_in, parse_date, today_in
from wall_tidbits.sources import load_riddles

TOKEN_ASSETS = ("daily.json", "display.json", "display.html", "credits.json")


async def get_or_build(app: FastAPI, day: date) -> dict:
    cached = app.state.cache.load(day)
    if cached is not None:
        return cached
    async with app.state.build_lock:
        cached = app.state.cache.load(day)
        if cached is not None:
            return cached
        payload = await builder.build_daily(
            day, app.state.settings, app.state.client, app.state.riddles
        )
        payload = builder.apply_last_good(payload, app.state.cache.load_last_good())
        if builder.worth_storing(payload):
            app.state.cache.store(day, payload)
        return payload


async def _refresh_loop(app: FastAPI) -> None:
    settings = app.state.settings
    while True:
        delay = (
            next_refresh_at(settings.timezone) - now_in(settings.timezone)
        ).total_seconds() + 1.0
        await asyncio.sleep(max(delay, 0))
        try:
            day = today_in(settings.timezone)
            async with app.state.build_lock:
                payload = await builder.build_daily(
                    day, settings, app.state.client, app.state.riddles
                )
                payload = builder.apply_last_good(payload, app.state.cache.load_last_good())
                if builder.worth_storing(payload):
                    app.state.cache.store(day, payload)
            app.state.cache.prune(settings.retention_days, day)
        except asyncio.CancelledError:
            raise
        except Exception:
            continue


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    try:
        ZoneInfo(settings.timezone)
    except Exception as exc:
        raise RuntimeError(f"unknown timezone {settings.timezone!r}") from exc

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.cache = DailyCache(settings.cache_dir)
        try:
            app.state.riddles = load_riddles(settings.riddles_path)
        except (OSError, ValueError) as exc:
            raise RuntimeError(f"cannot load riddles from {settings.riddles_path}") from exc
        app.state.client = httpx.AsyncClient(
            headers={"User-Agent": settings.effective_user_agent()},
            timeout=settings.fetch_timeout,
            follow_redirects=True,
        )
        app.state.build_lock = asyncio.Lock()
        refresh_task = None
        if settings.build_on_start:
            try:
                await get_or_build(app, today_in(settings.timezone))
            except Exception:
                pass
            refresh_task = asyncio.create_task(_refresh_loop(app))
        try:
            yield
        finally:
            if refresh_task is not None:
                refresh_task.cancel()
            await app.state.client.aclose()

    app = FastAPI(title="wall-tidbits", lifespan=lifespan)

    def resolve_day(value: str | None) -> date:
        try:
            day = parse_date(value, settings.timezone)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD") from exc
        today = today_in(settings.timezone)
        if day > today:
            raise HTTPException(status_code=400, detail="date is in the future")
        if day < today - timedelta(days=settings.retention_days):
            raise HTTPException(status_code=400, detail="date is outside the retention window")
        return day

    @app.get("/healthz")
    async def healthz() -> dict:
        return {"ok": True}

    @app.get("/")
    async def index() -> dict:
        return {
            "service": "wall-tidbits",
            "endpoints": [
                "/v1/daily",
                "/v1/display.json",
                "/v1/display.html",
                "/v1/credits",
                *[f"/e/{{token}}/{asset}" for asset in TOKEN_ASSETS],
            ],
        }

    @app.get("/v1/daily")
    async def daily(date: str | None = None) -> dict:
        return await get_or_build(app, resolve_day(date))

    @app.get("/v1/display.json")
    async def display_json(date: str | None = None) -> dict:
        return views.flat_view(await get_or_build(app, resolve_day(date)))

    @app.get("/v1/display.html", response_class=HTMLResponse)
    async def display_html(date: str | None = None) -> str:
        return html.render_display_html(views.flat_view(await get_or_build(app, resolve_day(date))))

    @app.get("/v1/credits")
    async def credits(date: str | None = None) -> dict:
        return views.credits_view(await get_or_build(app, resolve_day(date)))

    @app.get("/e/{token}/{asset}")
    async def public_asset(token: str, asset: str, date: str | None = None):
        if not settings.public_token:
            raise HTTPException(status_code=404)
        if not secrets.compare_digest(token, settings.public_token):
            raise HTTPException(status_code=404)
        if asset not in TOKEN_ASSETS:
            raise HTTPException(status_code=404)
        if asset == "daily.json":
            return await daily(date)
        if asset == "display.json":
            return await display_json(date)
        if asset == "display.html":
            return await display_html(date)
        return await credits(date)

    return app


app = create_app(load_settings())
