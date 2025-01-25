from matplotlib.patches import Rectangle

from .Chart import Chart

class Chart_ShaftViewer():
    def __init__(self, chart: Chart):
        self._chart = chart
        
        self._shaft_dimensions = []           # Stores dimensions of every shaft step
        self._bearings_dimensions = {}        # Stores dimensions of every bearing

        self._shaft_plot = []                 # Keeps track of shaft plot items
        self._shaft_dimensions_plot = []      # Keeps track of shaft dimensions plot items
        self._shaft_coordinates_plot = []     # Keeps track of shaft coordinates plot items
        self._bearings_plot = []              # Keeps track of bearings plot items
        self._shaft_markers = []              # Keeps track of shaft markers plot items

        self._dimension_offset = 0

        self._get_chart_controls()

    def _get_chart_controls(self):
        self._ax, self._canvas = self._chart.get_controls()

    def _set_axes_limits(self):
        """
        Set the axes limits for the plot based on the data.

        Get the shaft length from the points (last position) 
        and sets the axes limits.
        """
        shaft_length = self.points[-1]
        
        offset = 0.1 * shaft_length

        xlim = (-offset, shaft_length + offset)
        ylim = (-0.5 * (shaft_length + offset), 0.5 * (shaft_length + offset))

        self._ax.set_xlim(xlim)
        self._ax.set_ylim(ylim)

        self._chart.set_initial_axes_limits(xlim, ylim)
    
    def _get_dimension_offset(self):
        """
        Get the offset from the shaft that applies to shaft coordinates 
        and dimensions plots, so they get displayed neatly and do not
        overlay with shaft plot.
        """        
        highest_diameter = 0

        for step_dimensions in self._shaft_dimensions:
            step_diameter = step_dimensions['d']
            if step_diameter > highest_diameter:
                highest_diameter = step_diameter

        if highest_diameter != 0:
            self._dimension_offset = ((0.5 * highest_diameter ) * 1.2 + 5)

    def _draw_shaft_markers(self):
        """
        Draw the shaft characteristic points on the plot.

        This method adds markers and labels for significant points along the shaft,
        such as supports and eccentric positions.
        """        
        # Remove old markers
        for item in self._shaft_markers:
            item.remove()
        self._shaft_markers.clear()

        # Draw markers
        markers = self._ax.scatter(self.points, [0] * len(self.points),
                                   color=self._chart.markers_color,
                                   s=8,
                                   zorder=self._chart.markers_layer
                                   )
        self._shaft_markers.append(markers)
        
        # Draw labels for the markers
        for marker_coordinate, label in zip(self.points, self.labels):
            if len(label) > 1:
                label = label[0] + '_{' + ''.join(label[1:]) + '}'
            label = r'$\mathbf{' + label + '}$'
    
            annotation_label = self._ax.annotate(label, (marker_coordinate, 0), 
                                                  textcoords="offset points",
                                                  xytext=(10, -15),
                                                  ha='center',
                                                  color=self._chart.markers_color,
                                                  zorder=self._chart.markers_layer
                                                  )
            self._shaft_markers.append(annotation_label)
            
        self._canvas.draw()

        # Redraw shaft coordinates
        if self._shaft_coordinates_plot:
            self.draw_shaft_coordinates()

    def _draw_horizontal_dimension(self, text, start_z, end_z, label_z_position, y_position, item_y_position=0):
        lines = []

        # Draw dimension line
        dimension_line = self._ax.annotate('', xy=(start_z, y_position), xycoords='data',
                                           xytext=(end_z, y_position), textcoords='data',
                                           arrowprops=dict(arrowstyle="<->", color=self._chart.dimensions_color),
                                           zorder=self._chart.dimensions_layer
                                           )
        lines.append(dimension_line)

        # draw reference lines
        for position in [start_z, end_z]:
            reference_line = self._ax.plot([position, position], [item_y_position, y_position], 
                                            linestyle='-',
                                            linewidth=0.5,
                                            color=self._chart.dimensions_color,
                                            zorder=self._chart.reference_lines_layer
                                            )
            lines.append(reference_line[0])

        # Add dimension labels
        label_offset = 0.3
        label_y_position = y_position + label_offset
        ha, va = 'center', 'bottom'
        rotation = 0

        dimension_label = self._ax.text(label_z_position, label_y_position, text,
                                        rotation=rotation,
                                        ha=ha,
                                        va=va,
                                        fontsize=8,
                                        color=self._chart.dimensions_color,
                                        bbox=dict(alpha=0, zorder=self._chart.dimensions_layer)
                                        )
        lines.append(dimension_label)

        return lines

    def _draw_vertical_dimension(self, text, z_position, start_y, end_y, label_y_position, item_z_position=-1):
        lines = []

        # Draw dimension line
        dimension_line = self._ax.annotate('', xy=(z_position, start_y), xycoords='data',
                                           xytext=(z_position, end_y), textcoords='data',
                                           arrowprops=dict(arrowstyle="<->", color=self._chart.dimensions_color),
                                           zorder=self._chart.dimensions_layer
                                           )
        lines.append(dimension_line)

        # if it is eccentric dimension, draw additional point marking the middle (y) of the section
        if end_y == 0:
            middle_point = self._ax.scatter(z_position, start_y,
                                s=8,
                                color=self._chart.dimensions_color,
                                zorder=self._chart.dimensions_layer
                                )
            lines.append(middle_point)

        # draw reference lines
        if item_z_position >= 0:
            for position in [start_y, end_y]:
                reference_line = self._ax.plot([item_z_position, z_position], [position, position], 
                                                linestyle='-',
                                                linewidth=0.5,
                                                color=self._chart.dimensions_color,
                                                zorder=self._chart.reference_lines_layer
                                                )
                lines.append(reference_line[0])

        # draw reference lines
        offset = 0.3
        ha, va = 'right', 'center'
        rotation = 90
        label_z_position = z_position - offset

        # Add dimension labels
        dimension_label = self._ax.text(label_z_position, label_y_position, text,
                                        rotation=rotation,
                                        ha=ha,
                                        va=va,
                                        fontsize=8,
                                        color=self._chart.dimensions_color,
                                        bbox=dict(alpha=0, zorder=self._chart.dimensions_layer)
                                        )
        lines.append(dimension_label)
            
        return lines

    def _draw_dimension(self, text, start_z, end_z, label_z_position, start_y=0, end_y=0, label_y_position=0):
        lines = []

        # Draw dimension line
        dimension_line = self._ax.annotate('', xy=(start_z, start_y), xycoords='data',
                                           xytext=(end_z, end_y), textcoords='data',
                                           arrowprops=dict(arrowstyle="<->", color=self._chart.dimensions_color),
                                           zorder=self._chart.dimensions_layer
                                           )
        lines.append(dimension_line)

        # Perfrom actions depending of dimension line orientation
        offset = 0.3
        if start_z == end_z:                # Vertical line
            ha, va = 'right', 'center'
            rotation = 90
            label_z_position -= offset

            # if it is eccentric dimension, draw additional point marking the middle (y) of the section
            if end_y == 0:
                middle_point = self._ax.scatter(start_z, start_y,
                                   s=8,
                                   color=self._chart.dimensions_color,
                                   zorder=self._chart.dimensions_layer
                                   )
                lines.append(middle_point)            
        else:                               # Horizontal line
            ha, va = 'center', 'bottom'
            rotation = 0
            label_y_position += offset

            # draw reference lines for horizontal dimension lines
            for position in [start_z, end_z]:
                reference_line = self._ax.plot([position, position], [0.75 * end_y, end_y], 
                                               linestyle='-',
                                               linewidth=0.5,
                                               color=self._chart.dimensions_color,
                                               zorder=self._chart.dimensions_layer - 2
                                               )
                lines.append(reference_line[0])

        # Add dimension labels
        dimension_label = self._ax.text(label_z_position, label_y_position, text,
                                        rotation=rotation,
                                        ha=ha,
                                        va=va,
                                        fontsize=8,
                                        color=self._chart.dimensions_color,
                                        bbox=dict(alpha=0, zorder=self._chart.dimensions_layer)
                                        )
        lines.append(dimension_label)
        
        return lines

    def draw_shaft(self, shaft_dimensions):
        self._shaft_dimensions = shaft_dimensions

        # Remove old steps plots
        for step_plot in self._shaft_plot:
            step_plot.remove()
        self._shaft_plot.clear()

        # Plot new steps
        for step_dimensions in self._shaft_dimensions:
            start = step_dimensions['start']
            length = step_dimensions['l']
            diameter = step_dimensions['d']

            step_plot = Rectangle(start, length, diameter,
                                        linewidth=1,
                                        fill=True,
                                        edgecolor=self._chart.shaft_edge_color,
                                        facecolor=self._chart.shaft_face_color,
                                        zorder=self._chart.shaft_layer
                                        )
            self._shaft_plot.append(step_plot)
            self._ax.add_patch(step_plot)

        self._canvas.draw()

        # Redraw shaft dimensions
        if self._shaft_dimensions_plot:
            self.draw_shaft_dimensions()

    def init_shaft(self, coordinates):
        shaft_points = [('0',0)] + coordinates
        self.labels = [point[0] for point in shaft_points]
        self.points = [point[1] for point in shaft_points]

        self._set_axes_limits()
        self._draw_shaft_markers()
    
    def draw_shaft_dimensions(self):
        # Remove old dimensions
        self.remove_shaft_dimensions()

        # Draw new dimensions
        self._get_dimension_offset()

        for step_dimensions in self._shaft_dimensions:
            # Draw length dimension
            start = step_dimensions['start']
            length = step_dimensions['l']
            diameter = step_dimensions['d']

            start_z = start[0]
            end_z = start[0] + length
            y_position = self._dimension_offset
            label_position = start_z + length * 0.5
            item_y_position = start[1]
            text = "{:.1f}".format(length)

            length_dimension = self._draw_horizontal_dimension(text, start_z, end_z, label_position, y_position, item_y_position)
            self._shaft_dimensions_plot.extend(length_dimension)

            # Draw diameter dimension
            start_y = start[1]
            end_y = start[1] + diameter
            z_position = start_z + length * 0.75
            label_position = start_y + diameter * 0.5
            item_z_position = start[0]
            text = "Ø {:.1f}".format(diameter)

            diameter_dimension = self._draw_vertical_dimension(text, z_position, start_y, end_y, label_position, item_z_position)
            self._shaft_dimensions_plot.extend(diameter_dimension)

            # Draw eccentric
            if 'e' in step_dimensions:
                eccentric = step_dimensions['e']
                start_y = eccentric
                end_y = 0
                z_position = start_z + length * 0.5
                label_position = eccentric * 0.5
                item_z_position = start[0]
                text = "{:.1f}".format(abs(eccentric))

                diameter_dimension = self._draw_vertical_dimension(text, z_position, start_y, end_y, label_position)
                self._shaft_dimensions_plot.extend(diameter_dimension)

        self._canvas.draw()

    def draw_shaft_coordinates(self):
        # Remove old coordinates
        self.remove_shaft_coordinates()

        # Draw new coordinates
        self._get_dimension_offset()
        coordinates_dimension_offset = 5
        for i in range(len(self.points) - 1):
            start, end = 0, self.points[i + 1]
            mid_point = (start + end) / 2
            text = "{:.1f}".format(end - start)
            y_position = -self._dimension_offset - coordinates_dimension_offset * i
            item_y_position = 0

            dimension = self._draw_horizontal_dimension(text, start, end, mid_point, y_position, item_y_position)

            self._shaft_coordinates_plot.extend(dimension)
        
        self._canvas.draw()

    def set_bearings(self, bearings_dimensions):
        if bearings_dimensions:
            self._bearings_dimensions = bearings_dimensions

        if self._bearings_plot:
            self.draw_bearings()

    def draw_bearings(self):
        # Remove old bearings
        self.remove_bearings()
        
        # Draw new bearings
        for bearing in self._bearings_dimensions.values():
            for bearing_part in bearing.values():
                start = bearing_part['start']
                length = bearing_part['l']
                diameter = bearing_part['d']

                rim = Rectangle(start, length, diameter,
                                            linewidth=1,
                                            fill=True,
                                            edgecolor=self._chart.bearing_edge_color,
                                            facecolor=self._chart.bearing_face_color,
                                            zorder=self._chart.shaft_layer
                                            )
                self._ax.add_patch(rim)

                diagonal1 = self._ax.plot([start[0], start[0] + length], [start[1], start[1] + diameter], 
                                            linestyle='-',
                                            linewidth=1,
                                            color=self._chart.bearing_edge_color,
                                            zorder=self._chart.shaft_layer
                                            )
                diagonal2 = self._ax.plot([start[0] , start[0] + length], [start[1] + diameter, start[1] ], 
                                            linestyle='-',
                                            linewidth=1,
                                            color=self._chart.bearing_edge_color,
                                            zorder=self._chart.shaft_layer
                                            )

                self._bearings_plot.extend([rim, diagonal1[0], diagonal2[0]])
            
            d_in = abs(bearing[1]['start'][1]) + abs(bearing[0]['start'][1] + bearing[0]['d'])
            d_out = abs(bearing[1]['start'][1] + bearing[1]['d']) + abs(bearing[0]['start'][1])
            l = bearing[0]['l']

            # Draw length dimension
            start_z = bearing[0]['start'][0]
            end_z = start_z + l
            z_label_position = start_z + l * 0.5
            y_position = (d_out * 0.5) * 1.5
            item_y_position = bearing[1]['start'][1] + bearing[1]['d']
            text = "{:.1f}".format(l)

            dimension = self._draw_horizontal_dimension(text, start_z, end_z, z_label_position, y_position, item_y_position)
            self._bearings_plot.extend(dimension)

            # Draw inner diameter
            z_position = bearing[0]['start'][0] + l
            start_y = bearing[0]['start'][1] + bearing[0]['d']
            end_y = start_y + d_in
            y_label_position = start_y + d_in * 0.5
            item_z_position = bearing[0]['start'][0]
            text = "Ø {:.1f}".format(d_in)

            dimension = self._draw_vertical_dimension(text, z_position, start_y, end_y, y_label_position, item_z_position)
            self._bearings_plot.extend(dimension)

            # Draw outer diameter
            z_position = z_position + 2
            start_y = bearing[0]['start'][1]
            end_y = start_y + d_out
            y_label_position = start_y + d_out * 0.5
            text = "Ø {:.1f}".format(d_out)

            dimension = self._draw_vertical_dimension(text, z_position, start_y, end_y, y_label_position, item_z_position)
            self._bearings_plot.extend(dimension)
            
        self._canvas.draw()

    def remove_shaft_dimensions(self):
        # Remove dimensions
        for item in self._shaft_dimensions_plot:
            item.remove()
        self._shaft_dimensions_plot.clear()

        self._canvas.draw()

        # Redraw shaft coordinates
        if self._shaft_coordinates_plot:
            self.draw_shaft_coordinates()

    def remove_shaft_coordinates(self):
        # Remove coordinates
        for item in self._shaft_coordinates_plot:
            item.remove()
        self._shaft_coordinates_plot.clear()

        self._canvas.draw()

    def remove_bearings(self):
        for bearing in self._bearings_plot:
            bearing.remove()
        self._bearings_plot.clear()

        self._canvas.draw()
