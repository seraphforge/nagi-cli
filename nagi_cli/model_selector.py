"""Local Ollama model selector with persistent selection."""
from __future__ import annotations
import json
import os
from pathlib import Path
import httpx
import typer
from rich.console import Console

SETTINGS = Path(os.environ.get('NAGI_SETTINGS', '~/.config/nagi/settings.json')).expanduser()
BASE_URL = os.environ.get('OLLAMA_URL', 'http://127.0.0.1:11434').rstrip('/')
DEFAULT_MODEL = os.environ.get('NAGI_MODEL', 'qwen3:4b')
console = Console()


def current_model() -> str:
    if os.environ.get('NAGI_MODEL'):
        return os.environ['NAGI_MODEL']
    try:
        data = json.loads(SETTINGS.read_text(encoding='utf-8'))
        model = data.get('model')
        if isinstance(model, str) and model.strip():
            return model
    except (OSError, ValueError, TypeError):
        pass
    return DEFAULT_MODEL


def save_model(model: str) -> None:
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(SETTINGS.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            data = {}
    except (OSError, ValueError):
        data = {}
    data['model'] = model
    temp = SETTINGS.with_suffix('.json.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(SETTINGS)


def available_models() -> list[dict]:
    try:
        with httpx.Client(timeout=15, trust_env=False) as client:
            response = client.get(f'{BASE_URL}/api/tags')
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise RuntimeError(f'無法讀取 Ollama 模型：{exc}；請確認 ollama serve 已啟動') from exc
    models = data.get('models', [])
    if not isinstance(models, list):
        raise RuntimeError('Ollama 回傳的模型清單格式不正確')
    return sorted((m for m in models if isinstance(m, dict) and isinstance(m.get('name'), str)), key=lambda m: m['name'].lower())


def choose_model() -> str | None:
    models = available_models()
    if not models:
        console.print('[yellow]尚未安裝模型。請先執行 ollama pull qwen3:4b[/]')
        return None
    try:
        import questionary
    except ImportError as exc:
        raise RuntimeError('缺少互動選單套件：請執行 .venv/bin/python -m pip install questionary') from exc
    active = current_model()
    choices = []
    for m in models:
        size = m.get('size', 0)
        size_label = f'  ({size / (1024 ** 3):.1f} GiB)' if isinstance(size, (int, float)) and size > 0 else ''
        choices.append(questionary.Choice(title=f"{m['name']}{size_label}{'  ✓' if m['name'] == active else ''}", value=m['name']))
    chosen = questionary.select('選擇 Ollama 模型（↑↓ / Enter）', choices=choices, default=active if any(m['name'] == active for m in models) else None).ask()
    if chosen:
        save_model(chosen)
        console.print(f'[green]✓ 已選擇模型：{chosen}[/]')
    return chosen


def register(app: typer.Typer) -> None:
    @app.command('models')
    def models_command():
        """Choose an installed Ollama model using an arrow-key menu."""
        try:
            choose_model()
        except RuntimeError as exc:
            console.print(f'[red]{exc}[/]')
            raise typer.Exit(1)
