default_textcolor = (140, 230, 200)
group_bgcolor = (30, 0, 40)
button_bgcolor = (120, 60, 180)
button_textcolor = (230, 200, 255)
field_bgcolor = (60, 10, 80)
rendergroup_bordercolor = (160, 0, 190)

mayStyle = """

MainWindow {
    background-color: black;
}

QGroupBox {
    background-color: GROUP_BGCOLOR;
    border-radius: 10px;
    padding: 5px;
}

QGroupBox#renderGroup {
    background-color: GROUP_BGCOLOR;
    border: 4px solid;
    border-color: RENDERGROUP_BORDERCOLOR;
}

QGroupBox::title {
    color: DEFAULT_TEXTCOLOR;
}


QLabel, QCheckBox, QSlider {
    background-color: GROUP_BGCOLOR;
    color: DEFAULT_TEXTCOLOR;

}

QPushButton {
    background-color: BUTTON_BGCOLOR;
    color: BUTTON_TEXTCOLOR;
    font: 15px bold;
}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit, QListView {
    background-color: FIELD_BGCOLOR;
    color: DEFAULT_TEXTCOLOR;
    selection-background-color: BUTTON_BGCOLOR;
}

QListView::item {
    height: 17px;
}

/* damn u, KDE or whoever! */
QComboBox:selected, QComboBox:focus {
    background-color: BUTTON_BGCOLOR;
}

QComboBox QAbstractItemView {
    background-color: FIELD_BGCOLOR;
    color: DEFAULT_TEXTCOLOR;
    selection-background-color: BUTTON_BGCOLOR;
}

QComboBox QAbstractItemView:item {
    background-color: FIELD_BGCOLOR;
    color: DEFAULT_TEXTCOLOR;
    selection-background-color: BUTTON_BGCOLOR;
}

QSlider::handle {
    background-color: BUTTON_BGCOLOR;
}

QSlider::sub-page {
    background: BUTTON_BGCOLOR;
}

QSlider::add-page {
    background: black;
}

QProgressBar {
    background-color: black;
    color: DEFAULT_TEXTCOLOR;
}

"""\
    .replace('DEFAULT_TEXTCOLOR', 'rgb' + str(default_textcolor))\
    .replace('GROUP_BGCOLOR', 'rgb' + str(group_bgcolor))\
    .replace('BUTTON_BGCOLOR', 'rgb' + str(button_bgcolor))\
    .replace('BUTTON_TEXTCOLOR', 'rgb' + str(button_textcolor))\
    .replace('FIELD_BGCOLOR', 'rgb' + str(field_bgcolor))\
    .replace('RENDERGROUP_BORDERCOLOR', 'rgb' + str(rendergroup_bordercolor))
