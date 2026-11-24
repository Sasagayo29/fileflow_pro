from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from core.storage import ARQUIVOS_IGNORADOS


@dataclass
class AcaoArquivo:
    origem: Path
    destino: Path
    categoria: str
    tamanho: int
    renomeado: bool


@dataclass
class ResultadoAnalise:
    pasta_raiz: Path
    acoes: list[AcaoArquivo] = field(default_factory=list)
    agrupado: dict[str, list[AcaoArquivo]] = field(default_factory=dict)
    total_conflitos: int = 0
    total_ignorados: int = 0
    volume_total: int = 0


def analisar_diretorio(
    caminho: str,
    regras: dict[str, list[str]],
    incluir_outros: bool = True,
) -> ResultadoAnalise:
    raiz = Path(caminho)
    resultado = ResultadoAnalise(pasta_raiz=raiz)

    if not raiz.is_dir():
        return resultado

    mapa_ext = {
        ext.strip().lower(): cat
        for cat, extensoes in regras.items()
        for ext in extensoes
        if ext.strip()
    }

    agrupado: dict[str, list[AcaoArquivo]] = defaultdict(list)
    destinos_reservados: set[str] = set()

    for item in sorted(raiz.iterdir(), key=lambda p: p.name.lower()):
        if not item.is_file():
            resultado.total_ignorados += 1
            continue
        if item.name.lower() in ARQUIVOS_IGNORADOS or item.name.startswith("~$"):
            resultado.total_ignorados += 1
            continue

        ext = item.suffix.lower()
        categoria = mapa_ext.get(ext)

        if not categoria:
            if incluir_outros:
                categoria = "Outros"
            else:
                resultado.total_ignorados += 1
                continue

        pasta_destino = raiz / categoria
        destino_final = pasta_destino / item.name

        contador = 1
        while destino_final.exists() or str(destino_final).lower() in destinos_reservados:
            destino_final = pasta_destino / f"{item.stem} ({contador}){item.suffix}"
            contador += 1

        destinos_reservados.add(str(destino_final).lower())
        renomeado = destino_final.name != item.name
        if renomeado:
            resultado.total_conflitos += 1

        try:
            tamanho = item.stat().st_size
        except OSError:
            tamanho = 0

        resultado.volume_total += tamanho

        acao = AcaoArquivo(
            origem=item,
            destino=destino_final,
            categoria=categoria,
            tamanho=tamanho,
            renomeado=renomeado,
        )
        resultado.acoes.append(acao)
        agrupado[categoria].append(acao)

    resultado.agrupado = dict(sorted(agrupado.items(), key=lambda kv: kv[0].lower()))
    return resultado