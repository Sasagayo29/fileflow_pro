from PySide6.QtCore import (
    QEasingCurve, QPoint, QPropertyAnimation, QRect, QSize, Qt, QTimer,
    Property, Signal
)
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QFrame, QGraphicsDropShadowEffect, QHBoxLayout,
    QLabel, QLayout, QPushButton, QSizePolicy, QVBoxLayout, QWidget
)

from ui.icons import criar_icone


class ToggleSwitch(QCheckBox):
    """Interruptor animado moderno (substitui checkboxes genéricos em opções)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._offset = 3.0
        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.toggled.connect(self._animar)

    @Property(float)
    def offset(self) -> float:
        return self._offset

    @offset.setter
    def offset(self, valor: float):
        self._offset = valor
        self.update()

    def _animar(self, checked: bool):
        self._anim.stop()
        self._anim.setEndValue(21.0 if checked else 3.0)
        self._anim.start()

    def hitButton(self, pos: QPoint) -> bool:
        return self.rect().contains(pos)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Trilho
        if self.isChecked():
            track_color = QColor("#FFC107")
            border_color = QColor("#FFC107")
            knob_color = QColor("#090D16")
        else:
            track_color = QColor("#161F31")
            border_color = QColor("#334563")
            knob_color = QColor("#94A3B8")

        p.setPen(QPen(border_color, 1.2))
        p.setBrush(track_color)
        p.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 10, 10)

        # Botão circular (thumb)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(knob_color)
        p.drawEllipse(int(self._offset), 3, 16, 16)
        p.end()


class LabeledToggle(QWidget):
    """ToggleSwitch acompanhado de rótulo clicável."""
    toggled = Signal(bool)

    def __init__(self, texto: str, checked: bool = True, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.switch = ToggleSwitch()
        self.switch.setChecked(checked)
        self.switch.toggled.connect(self.toggled.emit)

        self.label = QLabel(texto)
        self.label.setStyleSheet("font-size: 12px; color: #CBD5E1; font-weight: 500;")
        self.label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.label.mousePressEvent = lambda _: self.switch.toggle()

        layout.addWidget(self.switch)
        layout.addWidget(self.label)

    def isChecked(self) -> bool:
        return self.switch.isChecked()


class KpiCard(QFrame):
    def __init__(self, titulo: str, icone: str, cor_icone: str = "#94A3B8", destaque: bool = False):
        super().__init__()
        self.setObjectName("KpiCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 13, 16, 13)
        layout.setSpacing(12)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setObjectName("KpiTitle")

        self.lbl_valor = QLabel("0")
        self.lbl_valor.setObjectName("KpiValueAccent" if destaque else "KpiValue")

        self.lbl_sub = QLabel("—")
        self.lbl_sub.setObjectName("KpiSub")

        text_col.addWidget(self.lbl_titulo)
        text_col.addWidget(self.lbl_valor)
        text_col.addWidget(self.lbl_sub)
        layout.addLayout(text_col, 1)

        icon_box = QFrame()
        icon_box.setObjectName("KpiIconBox")
        icon_box.setFixedSize(36, 36)
        ib_lay = QVBoxLayout(icon_box)
        ib_lay.setContentsMargins(0, 0, 0, 0)
        lbl_ico = QLabel()
        lbl_ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_ico.setPixmap(criar_icone(icone, cor_icone, 18).pixmap(18, 18))
        ib_lay.addWidget(lbl_ico)
        layout.addWidget(icon_box, 0, Qt.AlignmentFlag.AlignTop)

    def atualizar(self, valor: str, subtexto: str = ""):
        self.lbl_valor.setText(valor)
        self.lbl_sub.setText(subtexto or " ")


class StatusPill(QLabel):
    ESTILOS = {
        "success": ("rgba(16, 185, 129, 0.14)", "#34D399", "rgba(16, 185, 129, 0.32)"),
        "muted": ("rgba(100, 116, 139, 0.14)", "#94A3B8", "rgba(100, 116, 139, 0.30)"),
        "warning": ("rgba(255, 193, 7, 0.14)", "#FFC107", "rgba(255, 193, 7, 0.32)"),
    }

    def __init__(self, texto: str, variante: str = "success"):
        super().__init__(texto)
        bg, fg, border = self.ESTILOS.get(variante, self.ESTILOS["muted"])
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            f"background-color: {bg}; color: {fg}; border: 1px solid {border}; "
            "border-radius: 10px; padding: 2px 10px; font-size: 11px; font-weight: 700;"
        )


class FlowLayout(QLayout):
    """Layout com quebra automática de linha para chips/tags."""

    def __init__(self, parent=None, spacing: int = 8):
        super().__init__(parent)
        self._items = []
        self._spacing = spacing

    def addItem(self, item):
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect: QRect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        return size + QSize(m.left() + m.right(), m.top() + m.bottom())

    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        m = self.contentsMargins()
        eff = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x, y, line_h = eff.x(), eff.y(), 0

        for item in self._items:
            sz = item.sizeHint()
            next_x = x + sz.width() + self._spacing
            if next_x - self._spacing > eff.right() and line_h > 0:
                x = eff.x()
                y += line_h + self._spacing
                next_x = x + sz.width() + self._spacing
                line_h = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), sz))

            x = next_x
            line_h = max(line_h, sz.height())

        return y + line_h - rect.y() + m.bottom()


class ExtensionChip(QFrame):
    removido = Signal(str)

    def __init__(self, extensao: str):
        super().__init__()
        self.extensao = extensao
        self.setObjectName("ExtensionChip")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 6, 4)
        layout.setSpacing(6)

        lbl = QLabel(extensao)
        lbl.setObjectName("ChipText")
        layout.addWidget(lbl)

        btn = QPushButton()
        btn.setObjectName("ChipRemove")
        btn.setIcon(criar_icone("x", "#94A3B8", 12))
        btn.setIconSize(QSize(12, 12))
        btn.setFixedSize(18, 18)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.removido.emit(self.extensao))
        layout.addWidget(btn)


class DropZoneCard(QFrame):
    selecionar_clicado = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("DropZone")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        lbl_ico = QLabel()
        lbl_ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_ico.setPixmap(criar_icone("upload_cloud", "#FFC107", 44).pixmap(44, 44))
        layout.addWidget(lbl_ico)

        lbl_title = QLabel("Arraste uma pasta aqui para iniciar a simulação")
        lbl_title.setObjectName("DropTitle")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_sub = QLabel(
            "Nenhum arquivo será movido automaticamente. Você verá toda a árvore prevista antes de confirmar."
        )
        lbl_sub.setObjectName("DropSubtitle")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_sub)

        layout.addSpacing(6)

        btn = QPushButton("Selecionar Pasta no Computador")
        btn.setObjectName("PrimaryButton")
        btn.setIcon(criar_icone("folder_open", "#090D16", 15))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedWidth(250)
        btn.clicked.connect(self.selecionar_clicado.emit)
        layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignCenter)

    def definir_arrastando(self, ativo: bool):
        self.setProperty("dragging", "true" if ativo else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class ConfirmDialog(QDialog):
    def __init__(self, parent, titulo: str, mensagem: str, texto_confirmar: str = "Confirmar"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)

        card = QFrame()
        card.setObjectName("ModalCard")
        card.setFixedWidth(450)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 160))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)

        lbl_t = QLabel(titulo)
        lbl_t.setObjectName("ModalTitle")
        layout.addWidget(lbl_t)

        lbl_m = QLabel(mensagem)
        lbl_m.setObjectName("ModalBody")
        lbl_m.setWordWrap(True)
        layout.addWidget(lbl_m)

        layout.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("SecondaryButton")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton(texto_confirmar)
        btn_ok.setObjectName("PrimaryButton")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.clicked.connect(self.accept)

        row.addWidget(btn_cancel)
        row.addWidget(btn_ok)
        layout.addLayout(row)

        outer.addWidget(card)


class ToastNotification(QFrame):
    CORES = {
        "info": "#38BDF8",
        "success": "#10B981",
        "warning": "#FFC107",
        "error": "#EF4444",
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("Toast")
        self.hide()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 140))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 16, 10)
        layout.setSpacing(10)

        self.barra = QFrame()
        self.barra.setFixedWidth(4)
        layout.addWidget(self.barra)

        self.lbl_msg = QLabel("")
        self.lbl_msg.setObjectName("ToastText")
        self.lbl_msg.setWordWrap(True)
        self.lbl_msg.setMaximumWidth(370)
        layout.addWidget(self.lbl_msg)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def exibir(self, mensagem: str, tipo: str = "info", duracao_ms: int = 4200):
        cor = self.CORES.get(tipo, self.CORES["info"])
        self.barra.setStyleSheet(f"background-color: {cor}; border-radius: 2px;")
        self.lbl_msg.setText(mensagem)
        self.adjustSize()
        self.reposicionar()
        self.show()
        self.raise_()
        self.timer.start(duracao_ms)

    def reposicionar(self):
        if self.parent():
            p = self.parent()
            self.move(max(14, p.width() - self.width() - 22), max(14, p.height() - self.height() - 42))