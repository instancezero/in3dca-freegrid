#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate In3D.ca FreeGrid storage box components in FreeCAD.

*******************************************************************************
*   Copyright (c) 2022 In3D.ca
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

__Name__ = 'In3D.ca FreeGrid Storage System box'
__Comment__ = 'Generate In3D.ca FreeGrid storage boxes'
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
from FreeCAD import Placement, Rotation
from in3dca import h
import math
import Part


class StorageBox:
    def __init__(self):
        self.INSIDE_RIM_BOTTOM = 3.4
        self.INSIDE_RIM_WIDTH = 0.4
        self.MIN_FLOOR = 4.8
        self.STACK_ADJUSTMENT = 2.3
        self.WALL_THICKNESS = 2.0
        self.SUPPORT_THICKNESS = 1.0
        self.as_components = False
        self.cells_x = 1
        self.cells_y = 1
        self.corner_size = 5.0
        self.floor_support = True
        # Generate the front face
        self.closed_front = True
        # Number of areas within the box
        self.divisions = 0
        self.divider_width = 1.2
        self.floor_thickness = self.MIN_FLOOR
        self.grip_depth = 0.0
        # Set to make magnet holes
        self.magnets = True
        # Set if box magnets are only in the far corners
        self.magnets_corners_only = False
        # Internal: size of the current box
        self.size_x = 0
        self.size_y = 0
        self.size_z = 0
        # Grid spacing
        self.spacing = 50
        # Rail width is a "half rail" width
        self.rail_width = 5
        self.ramp = False
        self.unit_height = 10
        self.x_size = 1
        self.y_size = 1
        self.ramp_radius = 10

    # Create the outer frame for a box
    def box_frame(self):
        x = self.size_x - 2 * self.corner_size
        y = self.size_y - 2 * self.corner_size

        # Start by creating the four walls of the box
        wall_face = h.poly_to_face(self.wall_profile())
        new_box = wall_face.extrude(h.xyz(z=y))
        new_box.Placement = Placement(h.xyz(y=y + self.corner_size), Rotation(h.xyz(1), 90))

        right = wall_face.extrude(h.xyz(z=y))
        right.Placement = Placement(
            h.xyz(x=self.size_x, y=self.corner_size), Rotation(h.xyz(0.0, 1.0, 1.0), 180)
        )
        new_box = new_box.fuse(right)

        x_wall = wall_face.extrude(h.xyz(z=x))
        if self.closed_front:
            x_wall.Placement = Placement(h.xyz(self.corner_size), Rotation(h.xyz(1.0, 1.0, 1.0), 120))
            new_box = new_box.fuse(x_wall)
        else:
            x_ledge = h.poly_to_face(self.wall_profile(True)).extrude(h.xyz(z=x))
            x_ledge.Placement = Placement(h.xyz(self.corner_size), Rotation(h.xyz(1.0, 1.0, 1.0), 120))
            new_box = new_box.fuse(x_ledge)

        x_wall.Placement = Placement(
            h.xyz(x + self.corner_size, self.size_y), Rotation(h.xyz(-1.0, 1.0, 1.0), 240)
        )
        new_box = new_box.fuse(x_wall)

        # Merge in the four corners
        corner = self.corner()
        corner.Placement = Placement(h.xyz(), Rotation(h.xyz(1.0, 1.0, 1.0), 120))
        new_box = new_box.fuse(corner)

        corner.Placement = Placement(h.xyz(y=self.size_y), Rotation(h.xyz(1.0), 90))
        new_box = new_box.fuse(corner)

        corner.Placement = Placement(h.xyz(self.size_x), Rotation(h.xyz(0, -1.0, -1.0), 180))
        new_box = new_box.fuse(corner)

        corner.Placement = Placement(h.xyz(self.size_x, self.size_y), Rotation(h.xyz(-1.0, 1.0, 1.0), 240))
        new_box = new_box.fuse(corner)

        return new_box

    # Create a corner that connects two walls
    def corner(self):
        faces = []
        # Establish the z face and translate it to connect to the wall
        z_verticies = self.wall_profile()
        for i, p in enumerate(z_verticies):
            z_verticies[i] = p.add(h.xyz(z=self.corner_size))
        faces.append(h.poly_to_face(z_verticies))

        # Establish the x face and rotate/translate it to connect to the wall
        x_verticies = self.wall_profile()
        for i, p in enumerate(x_verticies):
            x_verticies[i] = DraftVecUtils.rotate(p, math.radians(-90), h.xyz(y=1)) \
                .add(h.xyz(self.corner_size))
        faces.append(h.poly_to_face(x_verticies))

        # Fill in the inside triangle
        faces.append(h.poly_to_face([x_verticies[1], x_verticies[2], z_verticies[2]], 1))

        # connect the wall faces on a diagonal
        for i in range(2, 12):
            faces.append(h.poly_to_face(
                [x_verticies[i], x_verticies[i + 1], z_verticies[i + 1], z_verticies[i]], 1)
            )

        # Fill the outside triangle
        faces.append(h.poly_to_face([x_verticies[13], x_verticies[12], z_verticies[12]], 1))

        corner = Part.makeSolid(Part.makeShell(faces))
        # debug
        #        for f in faces:
        #            Part.show(f)
        #        Part.show(corner, 'corner')
        return corner

    def dividers(self):
        if self.divisions <= 1:
            return []
        offset = self.divider_width / 2.0
        # Create the divider profile in the XZ plane, clockwise from top left
        # when looking toward +Y
        points = [
            h.xyz(-offset, self.WALL_THICKNESS, self.size_z - self.INSIDE_RIM_BOTTOM),
            h.xyz(offset, self.WALL_THICKNESS, self.size_z - self.INSIDE_RIM_BOTTOM),
            h.xyz(offset, self.WALL_THICKNESS, self.floor_thickness + 1.0),
            h.xyz(offset + 1.0, self.WALL_THICKNESS, self.floor_thickness),
            h.xyz(-offset - 1.0, self.WALL_THICKNESS, self.floor_thickness),
            h.xyz(-offset, self.WALL_THICKNESS, self.floor_thickness + 1.0),
        ]
        profile = h.poly_to_face(points, 1)
        divider = profile.extrude(h.xyz(y=self.size_y - 2 * self.WALL_THICKNESS))
        dividers = []
        spacing = self.size_x / self.divisions
        for i in range(1, self.divisions):
            divider.Placement = Placement(h.xyz(spacing * i), Rotation())
            dividers.append(copy.copy(divider))
        return dividers

    def floor(self, depth, width):
        s = self.spacing
        x = self.size_x - 2 * self.corner_size
        y = self.size_y - 2 * self.corner_size
        floor = Part.makeBox(x, y, self.floor_thickness, h.xyz(self.corner_size, self.corner_size))

        # If the floor is thick enough, cut out dead space
        if self.floor_thickness > 1.2:
            margin = 6
            for i in range(0, width):
                y = i * s + margin
                for w in range(0, depth):
                    x = w * s + margin
                    cutout = Part.makeBox(
                        s - 2 * margin, s - 2 * margin, self.floor_thickness - 1.2, h.xyz(x, y)
                    )
                    floor = floor.cut(cutout)

            if self.floor_support:
                t = self.SUPPORT_THICKNESS
                d = (s - 2 * self.corner_size) / 1.414
                di = d - 2*t
                floor_support = Part.makeBox(d, d, self.floor_thickness - 1.19, h.xyz(-d/2, -d/2))
                floor_support = floor_support.cut(Part.makeBox(di, di, self.floor_thickness - 1.2, h.xyz(-di/2, -di/2)))
                floor_support = floor_support.fuse(Part.makeBox(di, t, self.floor_thickness - 1.19, h.xyz(-di/2, -t/2)))
                floor_support = floor_support.fuse(Part.makeBox(t, di, self.floor_thickness - 1.19, h.xyz(-t/2, -di/2)))
                for i in range(0, width):
                    y = i * s
                    for w in range(0, depth):
                        x = w * s
                        floor_support.Placement = Placement(h.xyz(x + s/2, y + s/2), Rotation(h.xyz(z=1), 45))
                        floor = floor.fuse(floor_support)

        if self.magnets and self.floor_thickness >= 2.2 + 1.2:
            # Holders for magnets
            holder = self.magnet_holder(6)
            c = 10
            if self.magnets_corners_only:
                holder.Placement = Placement(h.xyz(c, c), Rotation())
                floor = floor.fuse(holder)
                holder.Placement = Placement(h.xyz(self.size_x - c, c), Rotation(h.xyz(z=1), 90))
                floor = floor.fuse(holder)
                holder.Placement = Placement(h.xyz(c, self.size_y - c), Rotation(h.xyz(z=1), 270))
                floor = floor.fuse(holder)
                holder.Placement = Placement(h.xyz(self.size_x - c, self.size_y - c), Rotation(h.xyz(z=1), 180))
                floor = floor.fuse(holder)
            else:
                for i in range(0, width):
                    y = i * s
                    for w in range(0, depth):
                        x = w * s
                        holder.Placement = Placement(h.xyz(x + c, y + c), Rotation())
                        floor = floor.fuse(holder)
                        holder.Placement = Placement(h.xyz(x + s - c, y + c), Rotation(h.xyz(z=1), 90))
                        floor = floor.fuse(holder)
                        holder.Placement = Placement(h.xyz(x + c, y + s - c), Rotation(h.xyz(z=1), 270))
                        floor = floor.fuse(holder)
                        holder.Placement = Placement(h.xyz(x + s - c, y + s - c), Rotation(h.xyz(z=1), 180))
                        floor = floor.fuse(holder)

        return floor

    # Create a grip / label area across the back of the box
    def grip_object(self):
        # Build the grip profile in the YZ plane
        back_wall = self.size_y - self.WALL_THICKNESS
        depth = self.grip_depth
        if self.size_z - self.INSIDE_RIM_BOTTOM - depth < self.floor_thickness + 1.0:
            depth = self.size_z - self.INSIDE_RIM_BOTTOM - (self.floor_thickness + 1.0)
        if depth <= 0:
            return None
        points = [
            h.xyz(self.WALL_THICKNESS, back_wall, self.size_z - self.INSIDE_RIM_BOTTOM),
            h.xyz(self.WALL_THICKNESS, back_wall - depth, self.size_z - self.INSIDE_RIM_BOTTOM),
            h.xyz(self.WALL_THICKNESS, back_wall - depth, self.size_z - self.INSIDE_RIM_BOTTOM - 1),
            h.xyz(self.WALL_THICKNESS, back_wall, self.size_z - self.INSIDE_RIM_BOTTOM - depth - 1),
            h.xyz(self.WALL_THICKNESS, back_wall, self.size_z - self.INSIDE_RIM_BOTTOM),
        ]
        grip = h.poly_to_face(points).extrude(h.xyz(self.size_x - 2 * self.WALL_THICKNESS))
        trim = self.corner_size + 0.5
        corner_face = h.poly_to_face([
            h.xyz(0, self.size_y), h.xyz(trim, self.size_y),
            h.xyz(0, self.size_y - trim), h.xyz(0, self.size_y)
        ])
        grip = grip.cut(corner_face.extrude(h.xyz(z=self.size_z)))
        corner_face = h.poly_to_face([
            h.xyz(self.size_x - trim, self.size_y),
            h.xyz(self.size_x, self.size_y),
            h.xyz(self.size_x, self.size_y - trim),
            h.xyz(self.size_x - trim, self.size_y),
        ])
        grip = grip.cut(corner_face.extrude(h.xyz(z=self.size_z)))

        return grip

    def inner_cut_profile(self):
        # counter-clockwise from left bottom bevel
        profile = [
            h.xyz(-3.0, z=0.0),
            h.xyz(3.0, z=0.0),  # Across the bottom
            h.xyz(2.5, z=0.5),  # Right lower bevel
            h.xyz(2.5, z=1.0),  # Right vertical edge
            h.xyz(0.5, z=3.0),  # 45 degrees to the top
            h.xyz(-0.5, z=3.0),  # Top face
            h.xyz(-2.5, z=1.0),  # 45 degrees to the left vertical edge
            h.xyz(-2.5, z=0.5),  # Left vertical edge
            h.xyz(-3.0, z=0.0),  # Left lower bevel back to the start
        ]
        return profile

    def insert_as_sketch(self, width, depth):
        if self.floor_thickness < self.MIN_FLOOR:
            self.floor_thickness = self.MIN_FLOOR
        self.cells_x = width
        self.cells_y = depth
        self.size_x = width * self.spacing
        self.size_y = depth * self.spacing
        points = [h.xyz(self.corner_size, self.WALL_THICKNESS)]
        if not self.closed_front:
            points.extend([
                h.xyz(self.corner_size, 0),
                h.xyz(self.size_x - self.corner_size, 0),
            ])

        points.extend([
            h.xyz(self.size_x - self.corner_size, self.WALL_THICKNESS),  # Across the bottom
            h.xyz(self.size_x - self.WALL_THICKNESS, self.corner_size),       # Up the LowerR corner bevel
            h.xyz(self.size_x - self.WALL_THICKNESS, self.size_y - self.corner_size),   # Up the right side
            h.xyz(self.size_x - self.corner_size, self.size_y - self.WALL_THICKNESS),   # The UpperR corner bevel
            h.xyz(self.corner_size, self.size_y - self.WALL_THICKNESS),       # R to L across the top
            h.xyz(self.WALL_THICKNESS, self.size_y - self.corner_size),       # The UpperL corner bevel
            h.xyz(self.WALL_THICKNESS, self.corner_size),           # Down the left side
            h.xyz(self.corner_size, self.WALL_THICKNESS),           # LowerL bevel to origin
        ])
        sketch = h.poly_to_sketch('box_' + str(self.cells_x) + " " + str(self.cells_y) + "_insert", points)
        sketch.Placement = Placement(h.xyz(z=self.floor_thickness), Rotation())
        return sketch

    # Create an object to introduce clearance at floor intersections
    def intersection(self):
        profile_master = self.inner_cut_profile()

        faces = []
        # Create four faces, each self.corner_size away from the origin. xp = x+, xn = x- etc.
        profile_yp = []
        for p in profile_master:
            profile_yp.append(h.xyz(p.x, self.corner_size, p.z))
        faces.append(h.poly_to_face(profile_yp))

        profile_yn = []
        for p in profile_master:
            profile_yn.append(h.xyz(p.x, -self.corner_size, p.z))
        faces.append(h.poly_to_face(profile_yn))

        profile_xp = []
        for p in profile_master:
            profile_xp.append(h.xyz(self.corner_size, p.x, p.z))
        faces.append(h.poly_to_face(profile_xp))

        profile_xn = []
        for p in profile_master:
            profile_xn.append(h.xyz(-self.corner_size, p.x, p.z))
        faces.append(h.poly_to_face(profile_xn))

        # Connect the faces diagonally
        for i in range(1, 4):  # will be 4
            j = 9 - i
            # Positive X to positive Y
            points = [
                profile_xp[i],
                profile_yp[i],
                profile_yp[i + 1],
                profile_xp[i + 1]
            ]
            faces.append(h.poly_to_face(points, 1))
            # Positive Y to Negative X
            points = [
                profile_yp[j],
                profile_xn[i],
                profile_xn[i + 1],
                profile_yp[j - 1],
            ]
            faces.append(h.poly_to_face(points, 1))
            # Negative X to negative Y
            points = [
                profile_xn[j],
                profile_yn[j],
                profile_yn[j - 1],
                profile_xn[j - 1],
            ]
            # print(points)
            faces.append(h.poly_to_face(points, 1))
            # Positive X to negative Y
            points = [
                profile_yn[i],
                profile_xp[j],
                profile_xp[j - 1],
                profile_yn[i + 1],
            ]
            faces.append(h.poly_to_face(points, 1))
        # Bottom face
        points = [
            profile_xp[1], profile_yp[1], profile_yp[8],
            profile_xn[1], profile_xn[8], profile_yn[8],
            profile_yn[1], profile_xp[8],
        ]
        faces.append(h.poly_to_face(points, 1))
        # Top face
        points = [
            profile_xp[4], profile_yp[4], profile_yp[5],
            profile_xn[4], profile_xn[5], profile_yn[5],
            profile_yn[4], profile_xp[5],
        ]
        faces.append(h.poly_to_face(points, 1))

        # debug
        #   for f in faces:
        #       Part.show(f)
        inter = Part.makeSolid(Part.makeShell(faces))
        #   Part.show(inter, 'inter')
        return inter

    def magnet_holder(self, mag_diameter):
        mag_radius = mag_diameter / 2.0
        peg_radius = mag_radius + 1.2
        holder = h.poly_to_face([
            h.xyz(),
            h.xyz(peg_radius, 0),
            h.xyz(peg_radius, -peg_radius),
            h.xyz(-peg_radius, -peg_radius),
            h.xyz(-peg_radius, peg_radius),
            h.xyz(0, peg_radius),
            h.xyz()
        ]).extrude(h.xyz(z=self.floor_thickness-0.01))
        holder = holder.fuse(h.disk(mag_radius + 1.2, self.floor_thickness-0.01))
        holder = holder.cut(h.disk(mag_radius + 0.1, 2.2))
        return holder

    def make(self, depth=1, width=1, height=1, floor_thickness=None):
        if floor_thickness is not None:
            self.floor_thickness = floor_thickness
        if self.floor_thickness < self.MIN_FLOOR:
            self.floor_thickness = self.MIN_FLOOR
        self.cells_x = depth
        self.cells_y = width
        self.size_x = depth * self.spacing
        self.size_y = width * self.spacing
        if height < 1:
            height = 1
        self.size_z = height * self.unit_height + self.STACK_ADJUSTMENT

        new_box = self.box_frame()

        # Add the floor
        new_box = new_box.fuse(self.floor(depth, width))

        # If there are dimensions larger than one, subtract room for the grids
        intersection = self.intersection()
        if depth > 1:
            cut = h.poly_to_face(self.inner_cut_profile()).extrude(h.xyz(y=self.size_y))
            for i in range(0, width + 1):
                intersection.Placement = Placement(h.xyz(0, i * self.spacing), Rotation())
                # Part.show(intersection)
                cut = cut.fuse(intersection)
            for w in range(1, depth):
                cut.Placement = Placement(h.xyz(w * self.spacing), Rotation())
                new_box = new_box.cut(cut)

        if width > 1:
            cut = h.poly_to_face(self.inner_cut_profile()).extrude(h.xyz(y=self.size_x))
            intersection.Placement = Placement(h.xyz(0, 0), Rotation())
            cut = cut.fuse(intersection)
            intersection.Placement = Placement(h.xyz(0, depth * self.spacing), Rotation())
            cut = cut.fuse(intersection)
            for i in range(1, width):
                cut.Placement = Placement(h.xyz(y=i * self.spacing), Rotation(h.xyz(z=1), -90))
                new_box = new_box.cut(cut)

        # Add the ramp at the front, if ordered
        if self.ramp and height > 1:
            ramp = self.ramp_object()
            if self.as_components:
                Part.show(ramp, 'Ramp')
            else:
                new_box = new_box.fuse(ramp)

        # Add any dividers
        for divider in self.dividers():
            if self.as_components:
                Part.show(divider, 'divider')
            else:
                new_box = new_box.fuse(divider)

        # Add the grip
        if self.grip_depth:
            grip = self.grip_object()
            if grip is not None:
                if self.as_components:
                    Part.show(grip, 'grip')
                else:
                    new_box = new_box.fuse(grip)

        return new_box

    # Create a circular ramp across the front of the box
    def ramp_object(self):
        # Get a quarter circle
        points = h.arc(self.ramp_radius, 90, 10)
        # close the polygon
        points.extend([h.xyz(self.ramp_radius, self.ramp_radius), h.xyz(0, self.ramp_radius)])
        ramp_face = h.poly_to_face(points)
        ramp = ramp_face.extrude(h.xyz(z=self.size_x - self.WALL_THICKNESS))
        ramp.Placement = Placement(h.xyz(1, 12.0, 14.8), Rotation(h.xyz(1, -1, 1), 240))
        trim = self.corner_size + 0.5
        corner_poly = h.poly_to_face([
            h.xyz(), h.xyz(trim), h.xyz(y=trim), h.xyz()
        ])
        ramp = ramp.cut(corner_poly.extrude(h.xyz(z=self.size_z)))
        corner_poly = h.poly_to_face([
            h.xyz(self.size_x - trim),
            h.xyz(self.size_x),
            h.xyz(self.size_x, trim),
            h.xyz(self.size_x - trim),
        ])
        ramp = ramp.cut(corner_poly.extrude(h.xyz(z=self.size_z)))

        return ramp

    def reset(self):
        self.as_components = False
        self.cells_x = 1
        self.cells_y = 1
        self.corner_size = 5.0
        # Generate the front face
        self.closed_front = True
        # Number of areas within the box
        self.divisions = 0
        self.divider_width = 1.2
        self.floor_thickness = self.MIN_FLOOR
        self.grip_depth = 0.0
        # Set to make magnet holes
        self.magnets = True
        # Set if box magnets are only in the far corners
        self.magnets_corners_only = False
        # Internal: size of the current box
        self.size_x = 0
        self.size_y = 0
        self.size_z = 0
        # Grid spacing
        self.spacing = 50
        # Rail width is a "half rail" width
        self.rail_width = 5
        self.ramp = False
        self.unit_height = 10
        self.x_size = 1
        self.y_size = 1
        self.ramp_radius = 10

    def self_test(self):
        # Generate test objects. Naming is x, y, z, divisions, options (open, magnet corners, no magnets, etc,)
        self.self_test_1x1(h.xyz())
        self.self_test_1x1_features(h.xyz(y=60))
        self.self_test_1x2(h.xyz(y=120))
        self.self_test_sketch(h.xyz(y=-60))

    def self_test_1x1(self, origin):
        shift = 0
        incr = 60
        self.reset()
        b1x1x1p1 = self.make()
        b1x1x1p1.Placement = Placement(origin.add(h.xyz(shift)), Rotation())
        Part.show(b1x1x1p1, 'b1x1x1p1')
        shift += incr

        self.reset()
        self.closed_front = False
        b1x1x1p1_of = self.make()
        b1x1x1p1_of.Placement = Placement(origin.add(h.xyz(shift)), Rotation())
        Part.show(b1x1x1p1_of, 'b1x1x1p1_of')
        shift += incr

        self.reset()
        self.magnets = False
        b1x1x1p1_nm = self.make()
        b1x1x1p1_nm.Placement = Placement(origin.add(h.xyz(shift, 50, 10)), Rotation(h.xyz(1), 180))
        Part.show(b1x1x1p1_nm, 'b1x1x1p1_nm')
        shift += incr

    def self_test_1x1_features(self, origin):
        shift = 0
        incr = 60

        self.reset()
        self.grip_depth = 15
        b1x1x1p1 = self.make()
        b1x1x1p1.Placement = Placement(origin.add(h.xyz(shift)), Rotation())
        Part.show(b1x1x1p1, 'b1x1x1p1_grip15')
        shift += incr

        self.reset()
        self.grip_depth = 15
        b1x1x3p1 = self.make(1, 1, 3)
        b1x1x3p1.Placement = Placement(origin.add(h.xyz(shift)), Rotation())
        Part.show(b1x1x3p1, 'b1x1x3p1_grip15')
        shift += incr

        self.reset()
        self.divisions = 2
        b1x1x1d2 = self.make()
        b1x1x1d2.Placement = Placement(origin.add(h.xyz(shift)), Rotation())
        Part.show(b1x1x1d2, 'b1x1x1d2')
        shift += incr

        self.reset()
        self.divisions = 3
        b1x1x3d3 = self.make(1, 1, 3)
        b1x1x3d3.Placement = Placement(origin.add(h.xyz(shift)), Rotation())
        Part.show(b1x1x3d3, 'b1x1x1d3')
        shift += incr

        self.reset()
        self.divisions = 3
        self.grip_depth = 15
        b1x1x3d3_grip = self.make(1, 1, 3)
        b1x1x3d3_grip.Placement = Placement(origin.add(h.xyz(shift)), Rotation())
        Part.show(b1x1x3d3_grip, 'b1x1x1d3_ramp')
        shift += incr

        self.reset()
        self.ramp = True
        b1x1x2p1_ramp = self.make(1, 1, 2)
        b1x1x2p1_ramp.Placement = Placement(origin.add(h.xyz(shift+50, 50)), Rotation(h.xyz(z=1), 180))
        Part.show(b1x1x2p1_ramp, 'b1x1x2p1_ramp')
        shift += incr

    def self_test_1x2(self, origin):
        shift = 0
        incr = 60
        self.reset()
        b1x2x1p1 = self.make(1, 2)
        b1x2x1p1.Placement = Placement(origin.add(h.xyz(shift)), Rotation())
        Part.show(b1x2x1p1, 'b1x2x1p1')
        shift += incr

        self.reset()
        self.divisions = 2
        b1x2x1p2 = self.make(1, 2)
        b1x2x1p2.Placement = Placement(origin.add(h.xyz(shift)), Rotation())
        Part.show(b1x2x1p2, 'b1x2x1p2')
        shift += incr

        self.reset()
        self.closed_front = False
        b1x2x1p1_of = self.make(1, 2)
        b1x2x1p1_of.Placement = Placement(origin.add(h.xyz(shift)), Rotation())
        Part.show(b1x2x1p1_of, 'b1x2x1p1_of')
        shift += incr

        self.reset()
        self.magnets_corners_only = True
        b1x2x1p1_mc = self.make(1, 2)
        b1x2x1p1_mc.Placement = Placement(origin.add(h.xyz(shift, 100, 10)), Rotation(h.xyz(1), 180))
        Part.show(b1x2x1p1_mc, 'b1x2x1p1_mc')
        shift += incr

        self.reset()
        self.magnets = False
        b1x2x1p1_nm = self.make(1, 2)
        b1x2x1p1_nm.Placement = Placement(origin.add(h.xyz(shift, 100, 10)), Rotation(h.xyz(1), 180))
        Part.show(b1x2x1p1_nm, 'b1x2x1p1_nm')
        shift += incr

    def self_test_sketch(self, origin):
        shift = 0
        incr = 60
        self.reset()
        s1x1 = self.insert_as_sketch(1, 1)
        s1x1.Placement = Placement(origin.add(h.xyz(shift)), Rotation())
        shift += incr

        self.reset()
        self.closed_front = False
        s1x1_open = self.insert_as_sketch(1, 1)
        s1x1_open.Placement = Placement(origin.add(h.xyz(shift)), Rotation())
        shift += incr

    def top_profile(self, origin, reverse=True):
        # Generate this clockwise, relative to the origin, which is the outside top of the box,
        # inset by the spacing margin of 0.1. The profile ends at the bottom of the bottom rim bevel.
        width_at_rim = self.WALL_THICKNESS + self.INSIDE_RIM_WIDTH
        points = [
            h.xyz(0.1, -0.1).add(origin),
            h.xyz(1.1, -0.1).add(origin),
            h.xyz(width_at_rim, -(width_at_rim - 1.0)).add(origin),
            h.xyz(width_at_rim, -self.INSIDE_RIM_BOTTOM).add(origin),
            h.xyz(self.WALL_THICKNESS, -self.INSIDE_RIM_BOTTOM - self.INSIDE_RIM_WIDTH).add(origin),
        ]
        if reverse:
            points.reverse()

        # FreeCAD.Console.PrintMessage("origin: (" + str(origin.x) + ", " + str(origin.y) + "),\n")
        # for p in points:
        #     FreeCAD.Console.PrintMessage("(" + str(p.x) + ", " + str(p.y) + "),\n")
        # FreeCAD.Console.PrintMessage("top profile end\n")

        return points

    def wall_profile(self, open_face=False):
        diagonal_end = max(self.floor_thickness, self.MIN_FLOOR)
        profile = [
            h.xyz(self.corner_size, 0.0),  # Bottom left
            h.xyz(self.corner_size, self.floor_thickness),  # Inside top of floor
            h.xyz(self.MIN_FLOOR, self.floor_thickness),  # to start of inner diagonal
            h.xyz(self.WALL_THICKNESS, diagonal_end),  # End of inner diagonal
        ]
        if open_face:
            profile.append(h.xyz(0.1, diagonal_end))
        else:
            profile.extend(self.top_profile(h.xyz(y=self.size_z)))
        profile.extend([
            h.xyz(0.1, 3.4),  # Down outer wall
            h.xyz(2.5, 1),  # Bottom outer diagonal
            h.xyz(2.5, 0.5),  #
            h.xyz(3.0, 0.0),  # Chamfer
            h.xyz(self.corner_size, 0.0),  # Return to origin
        ])
        return profile
