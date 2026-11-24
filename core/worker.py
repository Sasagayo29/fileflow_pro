import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from core.analyzer import AcaoArquivo


class WorkerOrganizacao(QThread):
    progresso = Signal(int, int, str)
    finalizado = Signal(dict)

    def __init__(self, pasta_raiz: str, acoes: list[AcaoArquivo]):
        super().__init__()
        self.pasta_raiz = pasta_raiz
        self.acoes = acoes

    def run(self):
        movidos = []
        pastas_criadas = []
        pastas_set = set()
        erros = []
        total = len(self.acoes)

        for idx, acao in enumerate(self.acoes, start=1):
            self.progresso.emit(idx, total, acao.origem.name)
            try:
                if not acao.origem.exists():
                    erros.append(f"{acao.origem.name}: arquivo não encontrado.")
                    continue

                if not acao.destino.parent.exists():
                    acao.destino.parent.mkdir(parents=True, exist_ok=True)
                    pasta_str = str(acao.destino.parent)
                    if pasta_str not in pastas_set:
                        pastas_set.add(pasta_str)
                        pastas_criadas.append(pasta_str)

                shutil.move(str(acao.origem), str(acao.destino))
                movidos.append({
                    "origem": str(acao.origem),
                    "destino": str(acao.destino),
                })
            except Exception as exc:
                erros.append(f"{acao.origem.name}: {exc}")

        registro = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "pasta": self.pasta_raiz,
            "movidos": movidos,
            "pastas_criadas": pastas_criadas,
            "erros": erros,
            "revertido": False,
        }
        self.finalizado.emit(registro)


class WorkerReversao(QThread):
    progresso = Signal(int, int, str)
    finalizado = Signal(int, int, str)

    def __init__(self, registro: dict):
        super().__init__()
        self.registro = registro

    def run(self):
        itens = list(reversed(self.registro.get("movidos", [])))
        total = len(itens)
        restaurados = 0
        falhas = 0

        for idx, par in enumerate(itens, start=1):
            origem = Path(par["origem"])
            destino = Path(par["destino"])
            self.progresso.emit(idx, total, destino.name)
            try:
                if destino.exists():
                    shutil.move(str(destino), str(origem))
                    restaurados += 1
            except Exception:
                falhas += 1

        for pasta_str in self.registro.get("pastas_criadas", []):
            pasta = Path(pasta_str)
            try:
                if pasta.exists() and not any(pasta.iterdir()):
                    pasta.rmdir()
            except Exception:
                pass

        self.finalizado.emit(restaurados, falhas, self.registro.get("id", ""))