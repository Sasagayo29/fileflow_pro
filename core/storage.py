import json
from pathlib import Path

APP_NAME = "FileFlow"
APP_EDITION = "PRO"
APP_VERSION = "2.0.0"

CONFIG_DIR = Path.home() / ".fileflow_pro"
ASSETS_DIR = CONFIG_DIR / "assets"
REGRAS_PATH = CONFIG_DIR / "regras.json"
HISTORICO_PATH = CONFIG_DIR / "historico.json"

CATEGORIAS_PADRAO: dict[str, list[str]] = {
    "Código": [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss",
        ".java", ".kt", ".c", ".cpp", ".cs", ".go", ".rs", ".php", ".rb",
        ".sql", ".json", ".xml", ".yaml", ".yml", ".sh", ".ps1", ".md", ".ipynb"
    ],
    "PDFs": [".pdf"],
    "Word e Documentos": [".doc", ".docx", ".odt", ".rtf", ".txt"],
    "Planilhas": [".xls", ".xlsx", ".xlsm", ".csv", ".ods"],
    "Apresentações": [".ppt", ".pptx", ".odp"],
    "Imagens": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico", ".psd"],
    "Vídeos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm"],
    "Áudios": [".mp3", ".wav", ".flac", ".ogg", ".m4a"],
    "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Executáveis": [".exe", ".msi", ".apk", ".bat"],
}

ARQUIVOS_IGNORADOS = {"desktop.ini", "thumbs.db", ".ds_store"}


def formatar_tamanho(num_bytes: int) -> str:
    valor = float(num_bytes)
    for unidade in ("B", "KB", "MB", "GB", "TB"):
        if valor < 1024.0:
            return f"{valor:.1f} {unidade}" if unidade != "B" else f"{int(valor)} B"
        valor /= 1024.0
    return f"{valor:.1f} PB"


def carregar_regras() -> dict[str, list[str]]:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if REGRAS_PATH.exists():
        try:
            with open(REGRAS_PATH, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if isinstance(dados, dict) and dados:
                    return dados
        except Exception:
            pass
    regras = {k: list(v) for k, v in CATEGORIAS_PADRAO.items()}
    salvar_regras(regras)
    return regras


def salvar_regras(regras: dict[str, list[str]]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(REGRAS_PATH, "w", encoding="utf-8") as f:
        json.dump(regras, f, ensure_ascii=False, indent=2)


def carregar_historico() -> list[dict]:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if HISTORICO_PATH.exists():
        try:
            with open(HISTORICO_PATH, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if isinstance(dados, list):
                    return dados
        except Exception:
            pass
    return []


def salvar_historico(historico: list[dict]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORICO_PATH, "w", encoding="utf-8") as f:
        json.dump(historico[:40], f, ensure_ascii=False, indent=2)