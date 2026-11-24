import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QFileDialog, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QProgressBar, QPushButton, QScrollArea, QStackedWidget,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget
)

from core.analyzer import AcaoArquivo, analisar_diretorio
from core.storage import (
    CATEGORIAS_PADRAO, formatar_tamanho, salvar_historico, salvar_regras
)
from core.worker import WorkerOrganizacao, WorkerReversao
from ui.icons import criar_icone
from ui.widgets import (
    ConfirmDialog, DropZoneCard, ExtensionChip, FlowLayout,
    KpiCard, LabeledToggle, StatusPill
)


# ==============================================================================
# TELA 1: ORGANIZADOR E SIMULAÇÃO (DRY-RUN)
# ==============================================================================
class OrganizerView(QWidget):
    status_alterado = Signal(str)
    notificar = Signal(str, str)
    execucao_concluida = Signal(dict)

    def __init__(self, get_regras_fn):
        super().__init__()
        self.get_regras = get_regras_fn
        self.pasta_atual = ""
        self.worker: WorkerOrganizacao | None = None
        self._montar_ui()

    def _montar_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 18)
        layout.setSpacing(14)

        # Cabeçalho + Toggle animado
        header = QHBoxLayout()
        col_title = QVBoxLayout()
        col_title.setSpacing(2)

        lbl_t = QLabel("Organizador de Diretórios")
        lbl_t.setObjectName("PageTitle")
        lbl_s = QLabel("Inspecione a árvore de destino, ajuste a seleção e aplique com reversão garantida.")
        lbl_s.setObjectName("PageSubtitle")
        col_title.addWidget(lbl_t)
        col_title.addWidget(lbl_s)
        header.addLayout(col_title)
        header.addStretch()

        self.toggle_outros = LabeledToggle("Agrupar desconhecidos em 'Outros'", checked=True)
        self.toggle_outros.toggled.connect(lambda _: self.analisar_pasta())
        header.addWidget(self.toggle_outros)
        layout.addLayout(header)

        # Barra de diretório
        path_card = QFrame()
        path_card.setObjectName("SurfaceCard")
        p_lay = QHBoxLayout(path_card)
        p_lay.setContentsMargins(12, 10, 12, 10)
        p_lay.setSpacing(10)

        self.input_caminho = QLineEdit()
        self.input_caminho.setPlaceholderText("Nenhum diretório selecionado...")
        self.input_caminho.setReadOnly(True)
        p_lay.addWidget(self.input_caminho, 1)

        btn_pasta = QPushButton("Selecionar Pasta")
        btn_pasta.setObjectName("PrimaryButton")
        btn_pasta.setIcon(criar_icone("folder_open", "#090D16", 15))
        btn_pasta.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pasta.clicked.connect(self.selecionar_pasta)
        p_lay.addWidget(btn_pasta)

        btn_atualizar = QPushButton("Reanalisar")
        btn_atualizar.setObjectName("SecondaryButton")
        btn_atualizar.setIcon(criar_icone("refresh", "#CBD5E1", 14))
        btn_atualizar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_atualizar.clicked.connect(self.analisar_pasta)
        p_lay.addWidget(btn_atualizar)

        layout.addWidget(path_card)

        # KPIs
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        self.kpi_arquivos = KpiCard("ARQUIVOS ELEGÍVEIS", "file", "#FFC107", destaque=True)
        self.kpi_pastas = KpiCard("PASTAS PREVISTAS", "folder", "#38BDF8")
        self.kpi_volume = KpiCard("VOLUME TOTAL", "hard_drive", "#A78BFA")
        self.kpi_seguranca = KpiCard("CONFLITOS / IGNORADOS", "shield", "#10B981")

        for card in (self.kpi_arquivos, self.kpi_pastas, self.kpi_volume, self.kpi_seguranca):
            kpi_row.addWidget(card, 1)
        layout.addLayout(kpi_row)

        # Stack: Empty DropZone <-> Árvore de Prévia
        self.preview_stack = QStackedWidget()

        self.drop_zone = DropZoneCard()
        self.drop_zone.selecionar_clicado.connect(self.selecionar_pasta)
        self.preview_stack.addWidget(self.drop_zone)

        # Container da árvore + toolbar
        tree_page = QWidget()
        tp_lay = QVBoxLayout(tree_page)
        tp_lay.setContentsMargins(0, 0, 0, 0)
        tp_lay.setSpacing(10)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        lbl_sec = QLabel("PRÉVIA DA ESTRUTURA FINAL")
        lbl_sec.setObjectName("SectionLabel")
        toolbar.addWidget(lbl_sec)

        btn_marcar = QPushButton("Marcar Tudo")
        btn_marcar.setObjectName("GhostButton")
        btn_marcar.setIcon(criar_icone("check_square", "#94A3B8", 13))
        btn_marcar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_marcar.clicked.connect(lambda: self._definir_todos_checks(True))
        toolbar.addWidget(btn_marcar)

        btn_desmarcar = QPushButton("Desmarcar")
        btn_desmarcar.setObjectName("GhostButton")
        btn_desmarcar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_desmarcar.clicked.connect(lambda: self._definir_todos_checks(False))
        toolbar.addWidget(btn_desmarcar)

        toolbar.addStretch()

        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Filtrar arquivos ou categorias...")
        self.input_busca.setFixedWidth(260)
        self.input_busca.addAction(
            criar_icone("search", "#64748B", 14),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.input_busca.textChanged.connect(self._filtrar_arvore)
        toolbar.addWidget(self.input_busca)

        btn_exp = QPushButton("Expandir")
        btn_exp.setObjectName("SecondaryButton")
        btn_exp.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exp.clicked.connect(lambda: self.tree.expandAll())
        toolbar.addWidget(btn_exp)

        btn_col = QPushButton("Recolher")
        btn_col.setObjectName("SecondaryButton")
        btn_col.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_col.clicked.connect(lambda: self.tree.collapseAll())
        toolbar.addWidget(btn_col)

        tp_lay.addLayout(toolbar)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels([
            "ESTRUTURA PREVISTA", "TAMANHO", "DESTINO / AÇÃO", "STATUS"
        ])
        self.tree.setAlternatingRowColors(True)
        self.tree.setAnimated(True)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tree.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.setColumnWidth(2, 240)
        self.tree.itemChanged.connect(self._atualizar_resumo_selecao)
        tp_lay.addWidget(self.tree, 1)

        self.preview_stack.addWidget(tree_page)
        layout.addWidget(self.preview_stack, 1)

        # Progresso e Rodapé
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        footer = QHBoxLayout()
        self.lbl_resumo = QLabel("Selecione uma pasta para gerar o plano de organização.")
        self.lbl_resumo.setObjectName("PageSubtitle")
        footer.addWidget(self.lbl_resumo)
        footer.addStretch()

        self.btn_executar = QPushButton("Executar Organização")
        self.btn_executar.setObjectName("SuccessButton")
        self.btn_executar.setIcon(criar_icone("play", "#042419", 14))
        self.btn_executar.setEnabled(False)
        self.btn_executar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_executar.clicked.connect(self._confirmar_e_executar)
        footer.addWidget(self.btn_executar)
        layout.addLayout(footer)

    def selecionar_pasta(self):
        caminho = QFileDialog.getExistingDirectory(self, "Selecionar Pasta para Análise")
        if caminho:
            self.definir_pasta(caminho)

    def definir_pasta(self, caminho: str):
        if os.path.isdir(caminho):
            self.pasta_atual = caminho
            self.input_caminho.setText(caminho)
            self.preview_stack.setCurrentIndex(1)
            self.analisar_pasta()

    def analisar_pasta(self):
        if not self.pasta_atual or not os.path.isdir(self.pasta_atual):
            return

        res = analisar_diretorio(
            self.pasta_atual,
            self.get_regras(),
            incluir_outros=self.toggle_outros.isChecked(),
        )

        self.tree.blockSignals(True)
        self.tree.clear()

        ico_pasta = criar_icone("folder", "#FFC107", 16)
        ico_arq = criar_icone("file", "#94A3B8", 15)
        fonte_bold = QFont()
        fonte_bold.setBold(True)

        novas_pastas = 0
        for categoria, itens in res.agrupado.items():
            pasta_existe = (res.pasta_raiz / categoria).exists()
            if not pasta_existe:
                novas_pastas += 1
            bytes_cat = sum(a.tamanho for a in itens)

            no_cat = QTreeWidgetItem([
                f"{categoria}  ({len(itens)})",
                formatar_tamanho(bytes_cat),
                f"/{categoria}",
                "Pasta existente" if pasta_existe else "Nova pasta",
            ])
            no_cat.setIcon(0, ico_pasta)
            no_cat.setFont(0, fonte_bold)
            no_cat.setFlags(
                no_cat.flags()
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsAutoTristate
            )
            no_cat.setCheckState(0, Qt.CheckState.Checked)
            no_cat.setForeground(3, QColor("#38BDF8" if not pasta_existe else "#94A3B8"))
            self.tree.addTopLevelItem(no_cat)

            for acao in itens:
                acao_txt = f"Renomear → {acao.destino.name}" if acao.renomeado else "Mover arquivo"
                status_txt = "Conflito resolvido" if acao.renomeado else "Pronto"

                no_arq = QTreeWidgetItem([
                    acao.origem.name,
                    formatar_tamanho(acao.tamanho),
                    acao_txt,
                    status_txt,
                ])
                no_arq.setIcon(0, ico_arq)
                no_arq.setFlags(no_arq.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                no_arq.setCheckState(0, Qt.CheckState.Checked)
                no_arq.setData(0, Qt.ItemDataRole.UserRole, acao)
                no_arq.setForeground(3, QColor("#FFC107" if acao.renomeado else "#34D399"))
                no_cat.addChild(no_arq)

            no_cat.setExpanded(True)

        self.tree.blockSignals(False)

        self.kpi_arquivos.atualizar(str(len(res.acoes)), "prontos na simulação")
        self.kpi_pastas.atualizar(str(len(res.agrupado)), f"{novas_pastas} nova(s) a criar")
        self.kpi_volume.atualizar(formatar_tamanho(res.volume_total), "sem duplicação em disco")
        self.kpi_seguranca.atualizar(
            f"{res.total_conflitos} / {res.total_ignorados}",
            "renomeados / ignorados",
        )
        self.progress.setValue(0)
        self._filtrar_arvore(self.input_busca.text())
        self._atualizar_resumo_selecao()

        if res.acoes:
            self.status_alterado.emit(
                f"Análise concluída em '{res.pasta_raiz.name}': {len(res.acoes)} arquivo(s) mapeado(s)."
            )
        else:
            self.status_alterado.emit(
                f"Nenhum arquivo solto elegível encontrado em '{res.pasta_raiz.name}'."
            )

    def _definir_todos_checks(self, marcado: bool):
        estado = Qt.CheckState.Checked if marcado else Qt.CheckState.Unchecked
        self.tree.blockSignals(True)
        for i in range(self.tree.topLevelItemCount()):
            no_cat = self.tree.topLevelItem(i)
            no_cat.setCheckState(0, estado)
            for j in range(no_cat.childCount()):
                no_cat.child(j).setCheckState(0, estado)
        self.tree.blockSignals(False)
        self._atualizar_resumo_selecao()

    def _filtrar_arvore(self, texto: str):
        termo = texto.strip().lower()
        for i in range(self.tree.topLevelItemCount()):
            no_cat = self.tree.topLevelItem(i)
            cat_match = termo in no_cat.text(0).lower()
            algum_visivel = False

            for j in range(no_cat.childCount()):
                no_arq = no_cat.child(j)
                match = (
                    not termo
                    or cat_match
                    or termo in no_arq.text(0).lower()
                    or termo in no_arq.text(2).lower()
                )
                no_arq.setHidden(not match)
                if match:
                    algum_visivel = True

            no_cat.setHidden(not algum_visivel)

    def _acoes_selecionadas(self) -> list[AcaoArquivo]:
        selecionadas: list[AcaoArquivo] = []
        for i in range(self.tree.topLevelItemCount()):
            no_cat = self.tree.topLevelItem(i)
            for j in range(no_cat.childCount()):
                no_arq = no_cat.child(j)
                if no_arq.checkState(0) == Qt.CheckState.Checked:
                    acao = no_arq.data(0, Qt.ItemDataRole.UserRole)
                    if acao:
                        selecionadas.append(acao)
        return selecionadas

    def _atualizar_resumo_selecao(self, *_):
        acoes = self._acoes_selecionadas()
        qtd = len(acoes)
        self.btn_executar.setEnabled(qtd > 0)
        if qtd > 0:
            vol = formatar_tamanho(sum(a.tamanho for a in acoes))
            self.btn_executar.setText(f"Executar Organização ({qtd})")
            self.lbl_resumo.setText(f"{qtd} arquivo(s) selecionado(s) ({vol}) — modo simulação ativo.")
        else:
            self.btn_executar.setText("Executar Organização")
            self.lbl_resumo.setText("Nenhum arquivo marcado para movimentação.")

    def _confirmar_e_executar(self):
        acoes = self._acoes_selecionadas()
        if not acoes:
            return

        pastas_qtd = len({a.categoria for a in acoes})
        dlg = ConfirmDialog(
            self.window(),
            titulo="Confirmar Movimentação",
            mensagem=(
                f"Mover {len(acoes)} arquivo(s) para {pastas_qtd} pasta(s) dentro de:\n\n"
                f"{self.pasta_atual}\n\n"
                "Todo o lote será registrado na Auditoria e poderá ser revertido com um clique."
            ),
            texto_confirmar="Mover Agora",
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        self.btn_executar.setEnabled(False)
        self.progress.setMaximum(len(acoes))
        self.progress.setValue(0)

        self.worker = WorkerOrganizacao(self.pasta_atual, acoes)
        self.worker.progresso.connect(self._ao_progredir)
        self.worker.finalizado.connect(self._ao_finalizar)
        self.worker.start()

    def _ao_progredir(self, atual: int, total: int, nome: str):
        self.progress.setValue(atual)
        self.status_alterado.emit(f"Organizando ({atual}/{total}): {nome}")

    def _ao_finalizar(self, registro: dict):
        movidos = len(registro["movidos"])
        erros = len(registro["erros"])

        if movidos > 0:
            self.execucao_concluida.emit(registro)

        self.analisar_pasta()

        if erros:
            self.notificar.emit(
                f"Concluído com avisos: {movidos} movido(s), {erros} falha(s) (arquivo em uso).",
                "warning",
            )
        else:
            self.notificar.emit(
                f"Sucesso: {movidos} arquivo(s) organizados e registrados na Auditoria.",
                "success",
            )


# ==============================================================================
# TELA 2: GESTOR DE REGRAS COM CHIPS VISUAIS
# ==============================================================================
class RulesView(QWidget):
    regras_alteradas = Signal()
    notificar = Signal(str, str)

    def __init__(self, regras: dict[str, list[str]]):
        super().__init__()
        self.regras = regras
        self.cat_atual: str | None = None
        self._montar_ui()
        self.recarregar_lista()

    def _montar_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 18)
        layout.setSpacing(14)

        lbl_t = QLabel("Regras e Categorias")
        lbl_t.setObjectName("PageTitle")
        lbl_s = QLabel("Crie pastas personalizadas e gerencie as extensões associadas por meio de tags.")
        lbl_s.setObjectName("PageSubtitle")
        layout.addWidget(lbl_t)
        layout.addWidget(lbl_s)

        body = QHBoxLayout()
        body.setSpacing(16)

        # Coluna esquerda: categorias
        left_card = QFrame()
        left_card.setObjectName("SurfaceCard")
        left_card.setFixedWidth(285)
        l_lay = QVBoxLayout(left_card)
        l_lay.setContentsMargins(14, 14, 14, 14)
        l_lay.setSpacing(10)

        lbl_sec = QLabel("CATEGORIAS CONFIGURADAS")
        lbl_sec.setObjectName("SectionLabel")
        l_lay.addWidget(lbl_sec)

        self.lista_cat = QListWidget()
        self.lista_cat.currentItemChanged.connect(self._ao_selecionar_cat)
        l_lay.addWidget(self.lista_cat, 1)

        add_row = QHBoxLayout()
        add_row.setSpacing(6)
        self.input_nova_cat = QLineEdit()
        self.input_nova_cat.setPlaceholderText("Nova pasta (ex: Financeiro)")
        self.input_nova_cat.returnPressed.connect(self._criar_categoria)
        add_row.addWidget(self.input_nova_cat, 1)

        btn_add = QPushButton()
        btn_add.setObjectName("PrimaryButton")
        btn_add.setIcon(criar_icone("plus", "#090D16", 15))
        btn_add.setFixedWidth(36)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._criar_categoria)
        add_row.addWidget(btn_add)
        l_lay.addLayout(add_row)

        body.addWidget(left_card)

        # Coluna direita: editor de chips
        right_card = QFrame()
        right_card.setObjectName("SurfaceCard")
        r_lay = QVBoxLayout(right_card)
        r_lay.setContentsMargins(20, 18, 20, 18)
        r_lay.setSpacing(12)

        top_r = QHBoxLayout()
        self.lbl_cat_titulo = QLabel("Selecione uma categoria")
        self.lbl_cat_titulo.setObjectName("PageTitle")
        top_r.addWidget(self.lbl_cat_titulo)
        top_r.addStretch()

        btn_excluir = QPushButton("Excluir Categoria")
        btn_excluir.setObjectName("DangerButton")
        btn_excluir.setIcon(criar_icone("trash", "#F87171", 14))
        btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_excluir.clicked.connect(self._excluir_categoria)
        top_r.addWidget(btn_excluir)
        r_lay.addLayout(top_r)

        # Input para adicionar extensões
        ext_row = QHBoxLayout()
        ext_row.setSpacing(8)
        self.input_nova_ext = QLineEdit()
        self.input_nova_ext.setPlaceholderText("Adicionar extensão (ex: .xml, .ofx, .pdf) e pressione Enter...")
        self.input_nova_ext.returnPressed.connect(self._adicionar_extensoes)
        ext_row.addWidget(self.input_nova_ext, 1)

        btn_add_ext = QPushButton("Adicionar")
        btn_add_ext.setObjectName("PrimaryButton")
        btn_add_ext.setIcon(criar_icone("plus", "#090D16", 14))
        btn_add_ext.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_ext.clicked.connect(self._adicionar_extensoes)
        ext_row.addWidget(btn_add_ext)
        r_lay.addLayout(ext_row)

        lbl_chips = QLabel("EXTENSÕES ASSOCIADAS")
        lbl_chips.setObjectName("SectionLabel")
        r_lay.addWidget(lbl_chips)

        # Área rolável com FlowLayout de chips
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: #090D16; border: 1px solid #1D283B; border-radius: 8px;")

        self.chips_container = QWidget()
        self.chips_container.setStyleSheet("background-color: transparent;")
        self.chips_layout = FlowLayout(self.chips_container, spacing=8)
        self.chips_layout.setContentsMargins(12, 12, 12, 12)
        scroll.setWidget(self.chips_container)
        r_lay.addWidget(scroll, 1)

        # Rodapé de regras
        foot_r = QHBoxLayout()
        foot_r.addStretch()
        btn_reset = QPushButton("Restaurar Categorias Padrão")
        btn_reset.setObjectName("SecondaryButton")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.clicked.connect(self._restaurar_padroes)
        foot_r.addWidget(btn_reset)
        r_lay.addLayout(foot_r)

        body.addWidget(right_card, 1)
        layout.addLayout(body, 1)

    def recarregar_lista(self, selecionar: str | None = None):
        self.lista_cat.clear()
        alvo_row = 0
        for idx, cat in enumerate(sorted(self.regras.keys())):
            item = QListWidgetItem(f"{cat}  ({len(self.regras[cat])})")
            item.setIcon(criar_icone("folder", "#FFC107", 15))
            item.setData(Qt.ItemDataRole.UserRole, cat)
            self.lista_cat.addItem(item)
            if selecionar and cat == selecionar:
                alvo_row = idx
        if self.lista_cat.count() > 0:
            self.lista_cat.setCurrentRow(alvo_row)

    def _ao_selecionar_cat(self, current: QListWidgetItem | None, _prev):
        if not current:
            self.cat_atual = None
            self.lbl_cat_titulo.setText("Selecione uma categoria")
            self._renderizar_chips([])
            return
        self.cat_atual = current.data(Qt.ItemDataRole.UserRole)
        self.lbl_cat_titulo.setText(self.cat_atual)
        self._renderizar_chips(self.regras.get(self.cat_atual, []))

    def _renderizar_chips(self, extensoes: list[str]):
        while self.chips_layout.count():
            item = self.chips_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for ext in sorted(extensoes):
            chip = ExtensionChip(ext)
            chip.removido.connect(self._remover_extensao)
            self.chips_layout.addWidget(chip)

    def _criar_categoria(self):
        nome = self.input_nova_cat.text().strip()
        if not nome:
            return
        if nome in self.regras:
            self.notificar.emit("Essa categoria já existe.", "warning")
            return
        self.regras[nome] = []
        salvar_regras(self.regras)
        self.input_nova_cat.clear()
        self.recarregar_lista(selecionar=nome)
        self.regras_alteradas.emit()
        self.notificar.emit(f"Categoria '{nome}' criada.", "success")

    def _adicionar_extensoes(self):
        if not self.cat_atual:
            return
        texto = self.input_nova_ext.text().strip()
        if not texto:
            return

        adicionadas = 0
        for parte in texto.replace(";", ",").replace(" ", ",").split(","):
            ext = parte.strip().lower()
            if not ext:
                continue
            if not ext.startswith("."):
                ext = f".{ext}"
            if ext not in self.regras[self.cat_atual]:
                self.regras[self.cat_atual].append(ext)
                adicionadas += 1

        self.input_nova_ext.clear()
        if adicionadas:
            salvar_regras(self.regras)
            self.recarregar_lista(selecionar=self.cat_atual)
            self.regras_alteradas.emit()
            self.notificar.emit(f"{adicionadas} extensão(ões) adicionada(s) em '{self.cat_atual}'.", "success")

    def _remover_extensao(self, ext: str):
        if self.cat_atual and ext in self.regras.get(self.cat_atual, []):
            self.regras[self.cat_atual].remove(ext)
            salvar_regras(self.regras)
            self.recarregar_lista(selecionar=self.cat_atual)
            self.regras_alteradas.emit()

    def _excluir_categoria(self):
        if not self.cat_atual:
            return
        cat = self.cat_atual
        dlg = ConfirmDialog(
            self.window(),
            titulo="Excluir Categoria",
            mensagem=f"Deseja remover a categoria '{cat}' e todas as suas associações de extensão?",
            texto_confirmar="Excluir",
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        del self.regras[cat]
        salvar_regras(self.regras)
        self.recarregar_lista()
        self.regras_alteradas.emit()
        self.notificar.emit(f"Categoria '{cat}' removida.", "info")

    def _restaurar_padroes(self):
        self.regras.clear()
        for k, v in CATEGORIAS_PADRAO.items():
            self.regras[k] = list(v)
        salvar_regras(self.regras)
        self.recarregar_lista()
        self.regras_alteradas.emit()
        self.notificar.emit("Regras padrão restauradas.", "info")


# ==============================================================================
# TELA 3: AUDITORIA E REVERSÃO ASSÍNCRONA
# ==============================================================================
class HistoryView(QWidget):
    lote_revertido = Signal(str)
    status_alterado = Signal(str)
    notificar = Signal(str, str)

    def __init__(self, historico: list[dict]):
        super().__init__()
        self.historico = historico
        self.worker: WorkerReversao | None = None
        self._montar_ui()
        self.atualizar_tabela()

    def _montar_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 18)
        layout.setSpacing(14)

        lbl_t = QLabel("Auditoria e Histórico")
        lbl_t.setObjectName("PageTitle")
        lbl_s = QLabel("Acompanhe cada lote executado e reverta movimentações com segurança a qualquer momento.")
        lbl_s.setObjectName("PageSubtitle")
        layout.addWidget(lbl_t)
        layout.addWidget(lbl_s)

        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels([
            "DATA / HORA", "DIRETÓRIO", "MOVIDOS", "STATUS", "AÇÃO"
        ])
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setShowGrid(False)

        hh = self.tabela.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.tabela, 1)

    def atualizar_tabela(self):
        self.tabela.setRowCount(0)
        for idx, reg in enumerate(self.historico):
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setRowHeight(row, 46)

            self.tabela.setItem(row, 0, QTableWidgetItem(reg.get("data_hora", "-")))
            self.tabela.setItem(row, 1, QTableWidgetItem(reg.get("pasta", "-")))
            self.tabela.setItem(row, 2, QTableWidgetItem(f"{len(reg.get('movidos', []))} arq."))

            revertido = reg.get("revertido", False)

            pill_wrap = QWidget()
            p_lay = QHBoxLayout(pill_wrap)
            p_lay.setContentsMargins(8, 6, 8, 6)
            p_lay.addWidget(
                StatusPill("Revertido", "muted") if revertido else StatusPill("Aplicado", "success")
            )
            self.tabela.setCellWidget(row, 3, pill_wrap)

            btn_wrap = QWidget()
            b_lay = QHBoxLayout(btn_wrap)
            b_lay.setContentsMargins(6, 6, 8, 6)
            btn = QPushButton("Reverter")
            btn.setObjectName("SecondaryButton")
            btn.setIcon(criar_icone("undo", "#CBD5E1" if not revertido else "#475569", 13))
            btn.setEnabled(not revertido)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, i=idx: self._solicitar_reversao(i))
            b_lay.addWidget(btn)
            self.tabela.setCellWidget(row, 4, btn_wrap)

    def _solicitar_reversao(self, idx: int):
        reg = self.historico[idx]
        if reg.get("revertido"):
            return

        dlg = ConfirmDialog(
            self.window(),
            titulo="Reverter Lote Executado",
            mensagem=(
                f"Devolver {len(reg['movidos'])} arquivo(s) para o local original e remover "
                "as pastas novas que ficarem vazias?"
            ),
            texto_confirmar="Reverter Lote",
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        self.worker = WorkerReversao(reg)
        self.worker.progresso.connect(
            lambda a, t, n: self.status_alterado.emit(f"Revertendo ({a}/{t}): {n}")
        )
        self.worker.finalizado.connect(self._ao_finalizar_reversao)
        self.worker.start()

    def _ao_finalizar_reversao(self, restaurados: int, falhas: int, reg_id: str):
        pasta_afetada = ""
        for reg in self.historico:
            if reg.get("id") == reg_id:
                reg["revertido"] = True
                pasta_afetada = reg.get("pasta", "")
                break

        salvar_historico(self.historico)
        self.atualizar_tabela()
        self.lote_revertido.emit(pasta_afetada)
        self.status_alterado.emit("Reversão concluída.")

        if falhas:
            self.notificar.emit(
                f"Reversão parcial: {restaurados} restaurado(s), {falhas} falha(s).", "warning"
            )
        else:
            self.notificar.emit(
                f"Lote revertido: {restaurados} arquivo(s) restaurados com sucesso.", "info"
            )