


from dtk.ui.theme import *






app_theme = Theme(os.path.join((os.path.dirname(os.path.realpath(__file__))), "../app_theme"))


def allocation(widget):
    cr = widget.window.cairo_create()
    # rect = widget.allocation
    rect = widget.get_allocation()
    return cr,rect.x, rect.y,rect.width,rect.height
