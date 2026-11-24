import os

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QStackedWidget, QVBoxLayout, QWidget
)

from core.storage import (
    APP_EDITION, APP_NAME, APP_VERSION,
    carregar_historico, carregar_regras, salvar_historico
)
from ui.icons import criar_icone
from ui.views import HistoryView, OrganizerView, RulesView
from ui.widgets import ToastNotification


class FileFlowWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_EDITION} — Gestão Inteligente de Diretórios")
        self.resize(1200, 740)
        self.setMinimumSize(980, 620)
        self.setAcceptDrops(True)

        self.regras = carregar_regras()
        self.historico = carregar_historico()

        self._montar_shell()
        self.toast = ToastNotification(self)
        self._atualizar_badges_nav()

    def _montar_shell(self):
        root = QWidget()
        root.setObjectName("RootWidget")
        self.setCentralWidget(root)

        root_lay = QVBoxLayout(root)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # === SIDEBAR ===
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(14, 18, 14, 16)
        sb_lay.setSpacing(6)

        # Marca
        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(6, 0, 6, 12)
        brand_row.setSpacing(8)

        lbl_logo = QLabel()
        lbl_logo.setPixmap(criar_icone("logo", "#FFC107", 22).pixmap(22, 22))
        brand_row.addWidget(lbl_logo)

        lbl_name = QLabel(APP_NAME)
        lbl_name.setObjectName("BrandTitle")
        brand_row.addWidget(lbl_name)

        lbl_pro = QLabel(APP_EDITION)
        lbl_pro.setObjectName("BrandBadge")
        brand_row.addWidget(lbl_pro)
        brand_row.addStretch()
        sb_lay.addLayout(brand_row)

        lbl_nav = QLabel("NAVEGAÇÃO")
        lbl_nav.setObjectName("SidebarSection")
        sb_lay.addWidget(lbl_nav)
        sb_lay.addSpacing(2)

        self.nav_buttons: list[tuple[QPushButton, str, str]] = []
        itens = [
            ("folder", "Organizador"),
            ("sliders", "Regras e Tags"),
            ("history", "Auditoria"),
        ]
        for idx, (icone, titulo) in enumerate(itens):
            btn = QPushButton(f"  {titulo}")
            btn.setObjectName("NavItem")
            btn.setIconSize(QSize(17, 17))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, i=idx: self._trocar_pagina(i))
            sb_lay.addWidget(btn)
            self.nav_buttons.append((btn, icone, titulo))

        sb_lay.addStretch()

        # Card informativo no rodapé da sidebar
        foot_card = QFrame()
        foot_card.setObjectName("SidebarFooterCard")
        fc_lay = QVBoxLayout(foot_card)
        fc_lay.setContentsMargins(12, 10, 12, 10)
        fc_lay.setSpacing(3)

        lbl_safe = QLabel("Dry-Run Protegido")
        lbl_safe.setStyleSheet("font-size: 11px; font-weight: 700; color: #34D399;")
        lbl_desc = QLabel("Simulação prévia obrigatória com reversão por lote.")
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("font-size: 10px; color: #64748B;")
        fc_lay.addWidget(lbl_safe)
        fc_lay.addWidget(lbl_desc)
        sb_lay.addWidget(foot_card)

        body.addWidget(sidebar)

        # === STACK DE TELAS ===
        self.stack = QStackedWidget()
        self.view_org = OrganizerView(lambda: self.regras)
        self.view_rules = RulesView(self.regras)
        self.view_hist = HistoryView(self.historico)

        self.stack.addWidget(self.view_org)
        self.stack.addWidget(self.view_rules)
        self.stack.addWidget(self.view_hist)
        body.addWidget(self.stack, 1)

        root_lay.addLayout(body, 1)

        # === STATUS BAR ===
        status_bar = QFrame()
        status_bar.setObjectName("StatusBar")
        status_bar.setFixedHeight(28)
        st_lay = QHBoxLayout(status_bar)
        st_lay.setContentsMargins(16, 0, 16, 0)

        self.lbl_status = QLabel("Pronto — selecione ou arraste uma pasta para simular.")
        self.lbl_status.setObjectName("StatusText")
        st_lay.addWidget(self.lbl_status)
        st_lay.addStretch()

        lbl_ver = QLabel(f"{APP_NAME} {APP_EDITION} v{APP_VERSION}")
        lbl_ver.setObjectName("StatusText")
        st_lay.addWidget(lbl_ver)
        root_lay.addWidget(status_bar)

        # Conexões entre módulos
        self.view_org.status_alterado.connect(self.lbl_status.setText)
        self.view_org.notificar.connect(lambda m, t: self.toast.exibir(m, t))
        self.view_org.execucao_concluida.connect(self._registrar_execucao)

        self.view_rules.notificar.connect(lambda m, t: self.toast.exibir(m, t))
        self.view_rules.regras_alteradas.connect(self._ao_alterar_regras)

        self.view_hist.status_alterado.connect(self.lbl_status.setText)
        self.view_hist.notificar.connect(lambda m, t: self.toast.exibir(m, t))
        self.view_hist.lote_revertido.connect(self._ao_reverter_lote)

        self._trocar_pagina(0)

    def _trocar_pagina(self, indice: int):
        self.stack.setCurrentIndex(indice)
        for i, (btn, icone, _) in enumerate(self.nav_buttons):
            ativo = i == indice
            btn.setProperty("active", "true" if ativo else "false")
            btn.setIcon(criar_icone(icone, "#FFC107" if ativo else "#64748B", 17))
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _atualizar_badges_nav(self):
        self.nav_buttons[1][0].setText(f"  Regras e Tags ({len(self.regras)})")
        ativos = sum(1 for r in self.historico if not r.get("revertido"))
        self.nav_buttons[2][0].setText(f"  Auditoria ({ativos})" if ativos else "  Auditoria")

    def _registrar_execucao(self, registro: dict):
        self.historico.insert(0, registro)
        salvar_historico(self.historico)
        self.view_hist.atualizar_tabela()
        self._atualizar_badges_nav()

    def _ao_alterar_regras(self):
        self._atualizar_badges_nav()
        self.view_org.analisar_pasta()

    def _ao_reverter_lote(self, pasta_afetada: str):
        self._atualizar_badges_nav()
        if self.view_org.pasta_atual == pasta_afetada:
            self.view_org.analisar_pasta()

    # Drag & Drop global
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and os.path.isdir(urls[0].toLocalFile()):
                self.view_org.drop_zone.definir_arrastando(True)
                event.acceptProposedAction()
                return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.view_org.drop_zone.definir_arrastando(False)

    def dropEvent(self, event):
        self.view_org.drop_zone.definir_arrastando(False)
        urls = event.mimeData().urls()
        if urls:
            caminho = urls[0].toLocalFile()
            if os.path.isdir(caminho):
                self._trocar_pagina(0)
                self.view_org.definir_pasta(caminho)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "toast") and self.toast.isVisible():
            self.toast.reposicionar()