from PySide2.QtWidgets import QWidget, QHBoxLayout, QGraphicsScene, \
        QGraphicsView, QGraphicsItemGroup
from PySide2.QtGui import QPen, QBrush, QLinearGradient, QPixmap, \
        QColor, QPainter, QFont
from PySide2.QtCore import Qt, QRectF, QSize, QPoint

import logging
l = logging.getLogger(name=__name__)
# l.setLevel('DEBUG')

class QTraceViewer(QWidget):
    TAG_SPACING = 50
    LEGEND_X = -50
    LEGEND_Y = 0
    LEGEND_WIDTH = 10

    TRACE_FUNC_X = 0
    TRACE_FUNC_Y = 0
    TRACE_FUNC_WIDTH = 50
    TRACE_FUNC_MINHEIGHT = 1000

    MARK_X = LEGEND_X
    MARK_WIDTH = TRACE_FUNC_X - LEGEND_X + TRACE_FUNC_WIDTH
    MARK_HEIGHT = 5
    def __init__(self, workspace, disasm_view, parent=None):
        super().__init__(parent)
        self.workspace = workspace
        self.disasm_view = disasm_view
        self._trace = None
        self.view = None
        self.scene = None
        self._trace_stat = None
        self.mark = None
        self.selected_ins = None


        self._init_widgets()

    def _init_widgets(self):
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)

        self.trace_func = QGraphicsItemGroup()
        self.scene.addItem(self.trace_func)

        self.legend = None

        layout = QHBoxLayout()
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
        self.setFixedWidth(500)

    def _show_legend(self):
        pen = QPen(Qt.transparent)

        gradient = QLinearGradient(self.LEGEND_X, self.LEGEND_Y,
                self.LEGEND_X, self.LEGEND_Y + self.legend_height)
        gradient.setColorAt(0.0, Qt.red)
        gradient.setColorAt(0.4, Qt.yellow)
        gradient.setColorAt(0.6, Qt.green)
        gradient.setColorAt(0.8, Qt.blue)
        brush = QBrush(gradient)

        self.legend = self.scene.addRect(self.LEGEND_X, self.LEGEND_Y,
                self.LEGEND_WIDTH, self.legend_height, pen, brush)

    def mark_instruction(self, addr):
        self.selected_ins = addr
        if self.mark is not None:
            self.scene.removeItem(self.mark)
        self.mark = QGraphicsItemGroup()
        self.scene.addItem(self.mark)

        positions = self._trace_stat.get_positions(addr)
        for p in positions:
            color = self._get_mark_color(p, self._trace_stat.count)
            y = self._get_mark_y(p, self._trace_stat.count)
            self.mark.addToGroup(self.scene.addRect(self.MARK_X, y, self.MARK_WIDTH,
                    self.MARK_HEIGHT, QPen(color), QBrush(color)))

    def _get_mark_color(self, i, total):
        return self.legend_img.pixelColor(self.LEGEND_WIDTH / 2,
                self.legend_height * i / total + 1)

    def _get_mark_y(self, i, total):
        return self.TRACE_FUNC_Y + self.trace_func_unit_height * i

    def _graphicsitem_to_pixmap(self, graph):
        if graph.scene() is not None:
            r = graph.boundingRect()
            pixmap = QPixmap(r.width(), r.height())
            pixmap.fill(QColor(0, 0, 0, 0));
            painter = QPainter(pixmap)
            painter.drawRect(r)
            graph.scene().render(painter, QRectF(), graph.sceneBoundingRect())
            return pixmap
        else:
            return None

    def _show_trace_func(self, show_func_tag):
        x = self.TRACE_FUNC_X
        y = self.TRACE_FUNC_Y
        prev_name = None
        for (bbl, func, name) in self._trace_stat.trace_func:
            l.debug('Draw function %x, %s', func, name)
            color = self._trace_stat.get_func_color(func)
            self.trace_func.addToGroup( self.scene.addRect(x, y,
                self.TRACE_FUNC_WIDTH, self.trace_func_unit_height,
                QPen(color), QBrush(color)))
            if show_func_tag is True and name != prev_name:
                tag = self.scene.addText(name, QFont('Times', 7))
                tag.setPos(x + self.TRACE_FUNC_WIDTH +
                        self.TAG_SPACING, y - tag.boundingRect().height() / 2)
                self.trace_func.addToGroup(tag)
                anchor = self.scene.addLine(
                        self.TRACE_FUNC_X + self.TRACE_FUNC_WIDTH, y,
                        x + self.TRACE_FUNC_WIDTH + self.TAG_SPACING, y)
                self.trace_func.addToGroup(anchor)
                prev_name = name
            y += self.trace_func_unit_height


    def _set_mark_color(self):
        pixmap = self._graphicsitem_to_pixmap(self.legend)
        self.legend_img = pixmap.toImage()
        for p in range(self._trace_stat.count):
            color = self._get_mark_color(p, self._trace_stat.count)
            self._trace_stat.set_mark_color(p, color)

    def set_trace(self, trace):
        self._trace_stat = trace
        l.debug('minheight: %d, count: %d', self.TRACE_FUNC_MINHEIGHT,
                self._trace_stat.count)
        if self.TRACE_FUNC_MINHEIGHT < self._trace_stat.count * 15:
            self.trace_func_unit_height = 15
            show_func_tag = True
        else:
            self.trace_func_unit_height = self.TRACE_FUNC_MINHEIGHT / self._trace_stat.count
            show_func_tag = True
        self.legend_height = self._trace_stat.count * self.trace_func_unit_height
        self._show_trace_func(show_func_tag)
        self._show_legend()
        self._set_mark_color()
        if self.selected_ins is not None:
            self.mark_instruction(self.selected_ins)

    def _at_legend(self, pos):
        x = pos.x()
        y = pos.y()
        if x > self.TRACE_FUNC_X and \
                x < self.TRACE_FUNC_X + self.TRACE_FUNC_WIDTH and \
                y > self.TRACE_FUNC_Y and \
                y < self.TRACE_FUNC_Y + self.legend_height:
            return True
        else:
            return False

    def _to_logical_pos(self, pos):
        x_offset = self.view.horizontalScrollBar().value()
        y_offset = self.view.verticalScrollBar().value()
        return QPoint(pos.x() + x_offset, pos.y() + y_offset)


    def _get_position(self, y):
        y_relative = y - self.legend_height
        return y_relative // self.trace_func_unit_height

    def _get_bbl_from_y(self, y):
        position = self._get_position(y)
        return self._trace_stat.get_bbl_from_position(position)

    def _get_func_from_y(self, y):
        position = self._get_position(y)
        func_name = self._trace_stat.get_func_from_position(position)
        return self.workspace.instance.cfg.kb.functions.function(name=func_name)

    def mousePressEvent(self, event):
        button = event.button()
        pos = self._to_logical_pos(event.pos())
        if button == Qt.LeftButton and self._at_legend(pos):
            func = self._get_func_from_y(pos.y())
            bbl_addr = self._get_bbl_from_y(pos.y())

            self.workspace.on_function_selected(func)
            self.disasm_view.toggle_instruction_selection(bbl_addr)
