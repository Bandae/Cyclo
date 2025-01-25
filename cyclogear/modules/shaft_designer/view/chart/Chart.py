from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

import numpy as np

class Chart(FigureCanvas):
    """
    A class representing a chart widget in a PyQt application.

    This class is responsible for creating and managing the chart display,
    including the plot selection and updating the plot display.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)        
        self.axes = self.figure.add_subplot(111)
        super(Chart, self).__init__(self.figure)
        self.setParent(parent)

        # Adjust subplot parameters to make the plot fill the figure canvas
        self.figure.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)

        # Set background color
        self._set_colors()

        # Remove axes spines, ticks and grid lines
        self._strip_canvas()

        # Draw axes lines
        self._draw_axes_lines()

    def _set_colors(self):
        # Set background color
        self.face_color = '#eeeeee'
        self.background_color = '#e5f2ff'

        self.figure.set_facecolor(self.face_color)
        self.axes.set_facecolor(self.background_color)

        # Set grid lines color
        self.axes.grid(True, color='white')

        # Set other items colors
        self.shaft_edge_color = '#66beb2'
        self.shaft_face_color = (138/255, 214/255, 204/255, 0.5)
        self.bearing_edge_color = '#6497b1'
        self.bearing_face_color = (151/255, 185/255, 203/255, 0.5)
        self.axes_color = '#f74040'
        self.dimensions_color = '#3B645B'
        self.markers_color = '#f97171'

        # Set zorder - order of layers
        self.reference_lines_layer = 2
        self.axes_layer = 2
        self.shaft_layer = 3
        self.plots_layer = 4
        self.markers_layer = 5
        self.dimensions_layer = 6

    def _strip_canvas(self):
        # Remove spines
        self.axes.spines[['right', 'top', 'bottom', 'left']].set_visible(False)

        # Remove x and y tick labels
        self.axes.set_xticklabels([])
        self.axes.set_yticklabels([])

        # Remove tick marks
        self.axes.tick_params(axis='both',
                              which='both',
                              length=0,
                              labelbottom=False,
                              labelleft=False
                              )

        # Add zoom and pan functionality
        zoom_factory(self.axes)
        pan_factory(self.axes)

    def _draw_axes_lines(self):
        '''
        Draw axes on the canvas.
        '''
        # Draw x line
        self.axes.axhline(y=0, color=self.axes_color, linewidth=1)
        self.figure.canvas.draw_idle()

    def set_initial_axes_limits(self, xlim, ylim):
        '''
        Save initial axes limits.

        Args:
            xlim (tuple): tuple (min, max) of x axis limits.
            ylim (tuple): tuple (min, max) of y axis limits.
        '''
        self.initial_xlim = xlim
        self.initial_ylim = ylim

    def reset_initial_view(self):
        '''
        Reset the plot view to its original view.
        '''
        self.axes.set_xlim(self.initial_xlim)
        self.axes.set_ylim(self.initial_ylim)
        
        self.axes.figure.canvas.draw_idle()

    def get_controls(self):
        return (self.axes, self.figure.canvas)

def zoom_factory(axis, base_scale=1.5, min_zoom_range=0.1, max_xlim=(0, 1000), max_ylim=(-500, 500)):
    """
    Returns zooming functionality to axis.
    """
    def zoom_fun(event):
        """Zoom when scrolling."""
        if event.inaxes == axis:
            cur_xlim = axis.get_xlim()
            cur_ylim = axis.get_ylim()
            xdata, ydata = event.xdata, event.ydata

            direction = -np.sign(event.step)
            scale_factor = np.power(base_scale, direction)

            # Calculate proposed new limits
            new_xlim = [xdata - (xdata - cur_xlim[0]) * scale_factor,
                        xdata + (cur_xlim[1] - xdata) * scale_factor]
            new_ylim = [ydata - (ydata - cur_ylim[0]) * scale_factor,
                        ydata + (cur_ylim[1] - ydata) * scale_factor]

            # Enforce zoom-in limit
            if (new_xlim[1] - new_xlim[0]) < min_zoom_range or (new_ylim[1] - new_ylim[0]) < min_zoom_range:
                return  # Prevent zooming in beyond the limit
            
            # Enforce zoom-out limit
            if max_xlim and (new_xlim[1] - new_xlim[0]) > (max_xlim[1] - max_xlim[0]):
                new_xlim = max_xlim
            if max_ylim and (new_ylim[1] - new_ylim[0]) > (max_ylim[1] - max_ylim[0]):
                new_ylim = max_ylim

            # Apply the new limits
            axis.set_xlim(new_xlim)
            axis.set_ylim(new_ylim)

            axis.figure.canvas.draw_idle()

    fig = axis.get_figure()
    fig.canvas.mpl_connect('scroll_event', zoom_fun)

def pan_factory(axis):
    """
    Returns panning functionality to axis.
    """
    def on_press(event):
        """Callback for mouse button press."""
        if event.button == 2:  # Middle mouse button
            axis._pan_start = (event.xdata, event.ydata)

    def on_release(event):
        """Callback for mouse button release."""
        axis._pan_start = None

    def on_motion(event):
        """Callback for mouse motion."""
        if event.button == 2 and axis._pan_start is not None:  # Middle mouse button
            if event.xdata is not None and event.ydata is not None:
                xdata_start, ydata_start = axis._pan_start
                dx = event.xdata - xdata_start
                dy = event.ydata - ydata_start
                xlim = axis.get_xlim()
                ylim = axis.get_ylim()
                axis.set_xlim([xlim[0] - dx, xlim[1] - dx])
                axis.set_ylim([ylim[0] - dy, ylim[1] - dy])
                
                axis.figure.canvas.draw_idle()

    fig = axis.get_figure()
    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('button_release_event', on_release)
    fig.canvas.mpl_connect('motion_notify_event', on_motion)
