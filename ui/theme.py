def gerar_stylesheet(assets: dict[str, str]) -> str:
    check_url = assets["check"]
    minus_url = assets["minus"]
    chev_right = assets["chevron_right"]
    chev_down = assets["chevron_down"]

    return f"""
* {{
    font-family: "Segoe UI", "Inter", sans-serif;
    outline: none;
}}

QMainWindow, QWidget#RootWidget {{
    background-color: #090D16;
    color: #E2E8F0;
}}

/* ============================================================================
   SIDEBAR CORPORATIVA
============================================================================ */
QFrame#Sidebar {{
    background-color: #0D121E;
    border-right: 1px solid #1A2334;
}}

QLabel#BrandTitle {{
    font-size: 16px;
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: 0.3px;
}}

QLabel#BrandBadge {{
    background-color: rgba(255, 193, 7, 0.14);
    color: #FFC107;
    border: 1px solid rgba(255, 193, 7, 0.35);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 0.8px;
}}

QLabel#SidebarSection {{
    font-size: 10px;
    font-weight: 700;
    color: #475569;
    letter-spacing: 1px;
    padding-left: 10px;
}}

QPushButton#NavItem {{
    background-color: transparent;
    color: #94A3B8;
    border: 1px solid transparent;
    border-radius: 7px;
    padding: 9px 12px;
    text-align: left;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#NavItem:hover {{
    background-color: #131B2B;
    color: #E2E8F0;
}}
QPushButton#NavItem[active="true"] {{
    background-color: #161F31;
    color: #F8FAFC;
    border: 1px solid #26344D;
}}

QFrame#SidebarFooterCard {{
    background-color: #111827;
    border: 1px solid #1E293B;
    border-radius: 8px;
}}

/* ============================================================================
   TIPOGRAFIA E CARDS
============================================================================ */
QLabel#PageTitle {{
    font-size: 19px;
    font-weight: 700;
    color: #F8FAFC;
}}
QLabel#PageSubtitle {{
    font-size: 12px;
    color: #8A99B0;
}}
QLabel#SectionLabel {{
    font-size: 10px;
    font-weight: 700;
    color: #64748B;
    letter-spacing: 0.9px;
}}

QFrame#SurfaceCard {{
    background-color: #101624;
    border: 1px solid #1D283B;
    border-radius: 10px;
}}

QFrame#KpiCard {{
    background-color: #101624;
    border: 1px solid #1D283B;
    border-radius: 10px;
}}
QFrame#KpiCard:hover {{
    border-color: #2B3B56;
}}
QLabel#KpiTitle {{
    font-size: 10px;
    font-weight: 700;
    color: #64748B;
    letter-spacing: 0.6px;
}}
QLabel#KpiValue {{
    font-size: 21px;
    font-weight: 800;
    color: #F8FAFC;
}}
QLabel#KpiValueAccent {{
    font-size: 21px;
    font-weight: 800;
    color: #FFC107;
}}
QLabel#KpiSub {{
    font-size: 11px;
    color: #64748B;
}}
QFrame#KpiIconBox {{
    background-color: #161F31;
    border: 1px solid #222E44;
    border-radius: 8px;
}}

/* ============================================================================
   DROP ZONE (EMPTY STATE)
============================================================================ */
QFrame#DropZone {{
    background-color: #0D1320;
    border: 2px dashed #24324A;
    border-radius: 12px;
}}
QFrame#DropZone[dragging="true"] {{
    background-color: rgba(255, 193, 7, 0.06);
    border: 2px dashed #FFC107;
}}
QLabel#DropTitle {{
    font-size: 15px;
    font-weight: 700;
    color: #E2E8F0;
}}
QLabel#DropSubtitle {{
    font-size: 12px;
    color: #64748B;
}}

/* ============================================================================
   INPUTS E BOTÕES
============================================================================ */
QLineEdit {{
    background-color: #090D16;
    border: 1px solid #233046;
    border-radius: 7px;
    padding: 8px 12px;
    color: #F1F5F9;
    font-size: 12px;
    selection-background-color: #FFC107;
    selection-color: #090D16;
}}
QLineEdit:hover {{
    border-color: #334563;
}}
QLineEdit:focus {{
    border: 1px solid #FFC107;
    background-color: #0B101B;
}}

QPushButton#PrimaryButton {{
    background-color: #FFC107;
    color: #090D16;
    border: none;
    border-radius: 7px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 700;
}}
QPushButton#PrimaryButton:hover {{
    background-color: #F5B800;
}}
QPushButton#PrimaryButton:pressed {{
    background-color: #D9A300;
}}
QPushButton#PrimaryButton:disabled {{
    background-color: #1A2334;
    color: #475569;
}}

QPushButton#SuccessButton {{
    background-color: #10B981;
    color: #042419;
    border: none;
    border-radius: 7px;
    padding: 9px 20px;
    font-size: 12px;
    font-weight: 700;
}}
QPushButton#SuccessButton:hover {{
    background-color: #059669;
    color: #ECFDF5;
}}
QPushButton#SuccessButton:disabled {{
    background-color: #1A2334;
    color: #475569;
}}

QPushButton#SecondaryButton {{
    background-color: #161F31;
    color: #CBD5E1;
    border: 1px solid #27354E;
    border-radius: 7px;
    padding: 7px 13px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#SecondaryButton:hover {{
    background-color: #1E293F;
    border-color: #3B4E70;
    color: #F8FAFC;
}}
QPushButton#SecondaryButton:disabled {{
    background-color: #101624;
    color: #475569;
    border-color: #1A2334;
}}

QPushButton#GhostButton {{
    background-color: transparent;
    color: #94A3B8;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 600;
}}
QPushButton#GhostButton:hover {{
    background-color: #161F31;
    color: #F8FAFC;
}}

QPushButton#DangerButton {{
    background-color: rgba(239, 68, 68, 0.08);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
    border-radius: 7px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#DangerButton:hover {{
    background-color: rgba(239, 68, 68, 0.18);
    border-color: #EF4444;
}}

/* ============================================================================
   CHECKBOXES VETORIAIS (QCheckBox e QTreeWidget)
============================================================================ */
QCheckBox::indicator, QTreeWidget::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1.5px solid #3B4C68;
    background-color: #090D16;
}}
QCheckBox::indicator:hover, QTreeWidget::indicator:hover {{
    border-color: #FFC107;
    background-color: #131C2E;
}}
QCheckBox::indicator:checked, QTreeWidget::indicator:checked {{
    background-color: #FFC107;
    border-color: #FFC107;
    image: url("{check_url}");
}}
QTreeWidget::indicator:indeterminate {{
    background-color: #EAB308;
    border-color: #EAB308;
    image: url("{minus_url}");
}}
QCheckBox::indicator:disabled, QTreeWidget::indicator:disabled {{
    background-color: #111827;
    border-color: #1E293B;
}}

/* ============================================================================
   TREEWIDGET, LISTWIDGET E TABLEWIDGET
============================================================================ */
QTreeWidget, QTableWidget, QListWidget {{
    background-color: #0D121E;
    border: 1px solid #1D283B;
    border-radius: 10px;
    color: #E2E8F0;
    font-size: 12px;
    alternate-background-color: #101624;
    padding: 4px;
}}

QTreeWidget::item, QListWidget::item {{
    padding: 6px 8px;
    border-radius: 5px;
    margin: 1px 2px;
}}
QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid #151E2E;
}}
QTreeWidget::item:hover, QTableWidget::item:hover, QListWidget::item:hover {{
    background-color: #151E30;
}}
QTreeWidget::item:selected, QTableWidget::item:selected, QListWidget::item:selected {{
    background-color: #1C283E;
    color: #FFC107;
}}

/* Setas modernas de expansão na árvore */
QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {{
    image: url("{chev_right}");
}}
QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {{
    image: url("{chev_down}");
}}

QHeaderView::section {{
    background-color: #111827;
    color: #64748B;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.6px;
    padding: 9px 10px;
    border: none;
    border-bottom: 1px solid #1D283B;
}}

/* ============================================================================
   CHIPS DE EXTENSÕES
============================================================================ */
QFrame#ExtensionChip {{
    background-color: #162033;
    border: 1px solid #26354D;
    border-radius: 6px;
}}
QFrame#ExtensionChip:hover {{
    border-color: #FFC107;
}}
QLabel#ChipText {{
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    font-weight: 600;
    color: #E2E8F0;
}}
QPushButton#ChipRemove {{
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 2px;
}}
QPushButton#ChipRemove:hover {{
    background-color: rgba(239, 68, 68, 0.2);
}}

/* ============================================================================
   BARRA DE PROGRESSO, STATUS BAR, MODAL E TOAST
============================================================================ */
QProgressBar {{
    background-color: #161F31;
    border: none;
    border-radius: 3px;
    max-height: 5px;
}}
QProgressBar::chunk {{
    background-color: #FFC107;
    border-radius: 3px;
}}

QFrame#StatusBar {{
    background-color: #0D121E;
    border-top: 1px solid #1A2334;
}}
QLabel#StatusText {{
    font-size: 11px;
    color: #64748B;
}}

QFrame#ModalCard {{
    background-color: #111827;
    border: 1px solid #2B3B56;
    border-radius: 12px;
}}
QLabel#ModalTitle {{
    font-size: 16px;
    font-weight: 700;
    color: #F8FAFC;
}}
QLabel#ModalBody {{
    font-size: 12px;
    color: #94A3B8;
}}

QFrame#Toast {{
    background-color: #131C2D;
    border: 1px solid #2A3A55;
    border-radius: 9px;
}}
QLabel#ToastText {{
    font-size: 12px;
    font-weight: 500;
    color: #F8FAFC;
}}

/* Scrollbars minimalistas */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: #26344D;
    min-height: 28px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: #3B4E70;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""