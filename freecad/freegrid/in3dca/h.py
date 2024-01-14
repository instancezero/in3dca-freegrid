#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper functions for FreeCad

*******************************************************************************
*   Copyright (c) 2020-2022 In3D.ca
*
*   This program is free software: you can redistribute it and/or modify it
*   under the terms of the GNU Affero General Public License as published by
*   the Free Software Foundation, either version 3 of the License, or (at your
*   option) any later version.
*
*   This program is distributed in the hope that it will be useful, but WITHOUT
*   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
*   FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
*   for more details.
*
*   You should have received a copy of the GNU Affero General Public License
*   along with this program. If not, see <https://www.gnu.org/licenses/>.
*******************************************************************************
"""

__Name__ = 'Helper functions for FreeCad'
__Comment__ = ''
__Author__ = "Alan Langford <prints@in3d.ca>"
__Version__ = 'See CHANGELOG'
__Date__ = ''
__License__ = 'GNU AGPLv3+'
__Web__ = 'https://in3d.ca'
__Wiki__ = ''
__Icon__ = ''
__Help__ = ''
__Status__ = ''
__Requires__ = ''
__Communication__ = ''
__Files__ = ''

import copy
import DraftVecUtils
import FreeCAD
from FreeCAD import Base
import math
import Part
import Sketcher


def arc(radius: float = 10, degrees: float = 360, increment: float = 5,
        start_deg: float = 0) -> list:
    """Create a list of Vectors forming an arc"""
    increment_rads = math.radians(increment)
    position_rads = math.radians(start_deg)
    increment_abs = math.fabs(increment)
    points = []
    while degrees >= 0:
        points.append(xyz(radius * math.sin(position_rads),
                          radius * math.cos(position_rads)))
        position_rads += increment_rads
        degrees -= increment_abs
    return points


def disk(radius: float, depth: float, at=None) -> Part.Shape:
    """ Create a solid disk """
    if at is None:
        at = xyz()
    wire = Part.Wire(Part.makeCircle(radius, at))
    face = Part.Face(wire)
    return face.extrude(xyz(0, 0, depth))


def get_edges_enclosed_by_box(base_shape: Part.Shape, origin: Base.Vector,
                              size: Base.Vector, fully_enclosed=True, show=False
                              ) -> list:
    """
    Get all edges of the base shape inside a box defined by origin and size
    If fully_enclosed is set, both edge endpoints must be in the box. If not,
    any edge with a vertex inside the box is selected.
    """
    enclosure = FreeCAD.BoundBox(origin, origin.add(size))
    if show:
        box = Part.show(Part.makeBox(size.x, size.y, size.z, origin))
        box.ViewObject.DisplayMode = 'Wireframe'
    edge_list = []
    # Note, the isInside() method is misnamed. Actual function is "contains"
    for i, edge in enumerate(base_shape.Edges):
        if fully_enclosed:
            if enclosure.isInside(edge.BoundBox):
                edge_list.append(i)
        else:
            if enclosure.isInside(edge.Vertexes[0].Point) \
                or enclosure.isInside(edge.Vertexes[1].Point):
                edge_list.append(i)
    return edge_list


def poly_close(vec, to_origin=0) -> list[Base.Vector]:
    """
    Move a list of vertices to a new origin and if the list isn't a closed polygon,
    close it.
    """
    if to_origin == 0:
        to_origin = xyz()
    moved = []
    for point in vec:
        moved.append(xyz(point.x + to_origin.x, point.y + to_origin.y,
                         point.z + to_origin.z))

    last = len(moved) - 1
    if moved[0].x != moved[last].x or moved[0].y != moved[last].y \
        or moved[0].z != moved[last].z:
        moved.append(copy.copy(moved[0]))
    return moved


def poly_rotate(list, degrees, axis) -> list:
    """Rotate a list of points"""
    for i, p in enumerate(list):
        list[i] = DraftVecUtils.rotate(p, math.radians(degrees), axis)
    return list


def poly_to_face(points, close=0) -> Part.Face:
    """Convert polygon to face"""
    if close != 0:
        points = poly_close(points)

    return Part.Face(Part.makePolygon(points))


def poly_to_sketch(name, points, close=0) -> Part.Feature:
    """Convert points to sketch"""
    if close != 0:
        points = poly_close(points)

    doc = FreeCAD.ActiveDocument
    sketch = doc.addObject('Sketcher::SketchObject', name)
    last_index = len(points) - 1
    for i in range(last_index):
        sketch.addGeometry(Part.LineSegment(points[i], points[i + 1]))
        if i:
            sketch.addConstraint(Sketcher.Constraint('Coincident', i - 1, 2, i, 1))
        sketch.addConstraint(Sketcher.Constraint('DistanceX', i, 1, points[i].x))
        sketch.addConstraint(Sketcher.Constraint('DistanceY', i, 1, points[i].y))
    sketch.addConstraint(Sketcher.Constraint('Coincident', last_index - 1, 2, 0, 1))
    sketch.MapMode = 'FlatFace'
    doc.recompute()
    return sketch


def poly_translate(list, vector) -> list:
    """Translate a list of points"""
    for i, p in enumerate(list):
        list[i] = p.add(vector)
    return list


def xyz(x=0.0, y=0.0, z=0.0) -> Base.Vector:
    """Make a Vector with optional arguments"""
    return Base.Vector(x, y, z)
