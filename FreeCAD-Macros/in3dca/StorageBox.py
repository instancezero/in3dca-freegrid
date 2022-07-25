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
        self.MIN_FLOOR = 4.8
        self.RIM_BOTTOM = 4.1
        self.WALL_THICKNESS = 2.0
        self.as_components = False
        self.corner_size = 5.0
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
        x_wall.Placement = Placement(h.xyz(self.corner_size), Rotation(h.xyz(1.0, 1.0, 1.0), 120))
        new_box = new_box.fuse(x_wall)

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
            h.xyz(-offset, self.WALL_THICKNESS, self.size_z - self.RIM_BOTTOM),
            h.xyz(offset, self.WALL_THICKNESS, self.size_z - self.RIM_BOTTOM),
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

    def floor(self, width, length):
        s = self.spacing
        x = self.size_x - 2 * self.corner_size
        y = self.size_y - 2 * self.corner_size
        floor = Part.makeBox(x, y, self.floor_thickness, h.xyz(self.corner_size, self.corner_size))

        # If the floor is thick enough, cut out dead space
        if self.floor_thickness > 1.2:
            margin = 6
            for i in range(0, length):
                y = i * s + margin
                for w in range(0, width):
                    x = w * s + margin
                    cutout = Part.makeBox(
                        s - 2 * margin, s - 2 * margin, self.floor_thickness - 1.2, h.xyz(x, y)
                    )
                    floor = floor.cut(cutout)

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
                for i in range(0, length):
                    y = i * s
                    for w in range(0, width):
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
        if self.size_z - self.RIM_BOTTOM - depth < self.floor_thickness:
            depth = self.size_z - self.RIM_BOTTOM - self.floor_thickness
        if depth <= 0:
            return None
        points = [
            h.xyz(self.WALL_THICKNESS, back_wall, self.size_z - self.RIM_BOTTOM),
            h.xyz(self.WALL_THICKNESS, back_wall - depth, self.size_z - self.RIM_BOTTOM),
            h.xyz(self.WALL_THICKNESS, back_wall, self.size_z - self.RIM_BOTTOM - depth),
            h.xyz(self.WALL_THICKNESS, back_wall, self.size_z - self.RIM_BOTTOM),
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
        ]).extrude(h.xyz(z=self.floor_thickness))
        holder = holder.fuse(h.disk(mag_radius + 1.2, self.floor_thickness))
        holder = holder.cut(h.disk(mag_radius + 0.1, 2.2))
        return holder

    def make(self, width=1, length=1, height=1, floor_thickness=None):
        if floor_thickness is not None:
            self.floor_thickness = floor_thickness
        self.size_x = width * self.spacing
        self.size_y = length * self.spacing
        if height < 1:
            height = 1
        self.size_z = height * self.unit_height

        new_box = self.box_frame()

        # Add the floor
        new_box = new_box.fuse(self.floor(width, length))

        # If there are dimensions larger than one, subtract room for the grids
        intersection = self.intersection()
        if width > 1:
            cut = h.poly_to_face(self.inner_cut_profile()).extrude(h.xyz(y=self.size_y))
            for i in range(0, length + 1):
                intersection.Placement = Placement(h.xyz(0, i * self.spacing), Rotation())
                # Part.show(intersection)
                cut = cut.fuse(intersection)
            for w in range(1, width):
                cut.Placement = Placement(h.xyz(w * self.spacing), Rotation())
                new_box = new_box.cut(cut)

        if length > 1:
            cut = h.poly_to_face(self.inner_cut_profile()).extrude(h.xyz(y=self.size_x))
            intersection.Placement = Placement(h.xyz(0, 0), Rotation())
            cut = cut.fuse(intersection)
            intersection.Placement = Placement(h.xyz(0, width * self.spacing), Rotation())
            cut = cut.fuse(intersection)
            for i in range(1, length):
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

    def wall_profile(self):
        diagonal_end = max(self.floor_thickness, self.MIN_FLOOR)
        profile = [
            h.xyz(self.corner_size, 0.0),  # Bottom left
            h.xyz(self.corner_size, self.floor_thickness),  # Inside top of floor
            h.xyz(self.MIN_FLOOR, self.floor_thickness),  # to start of inner diagonal
            h.xyz(self.WALL_THICKNESS, diagonal_end),  # End of inner diagonal
            h.xyz(self.WALL_THICKNESS, self.size_z - 4.5),  # Up inner wall
            h.xyz(2.4, self.size_z - self.RIM_BOTTOM),  # Bottom rim diagonal
            h.xyz(2.4, self.size_z - 1.9),  # Inside rim
            h.xyz(1.1, self.size_z - 0.1),  # Top rim diagonal
            h.xyz(0.1, self.size_z - 0.1),  # Top flat
            h.xyz(0.1, 3.4),  # Down outer wall
            h.xyz(2.5, 1),  # Bottom outer diagonal
            h.xyz(2.5, 0.5),  #
            h.xyz(3.0, 0.0),  # Chamfer
            h.xyz(self.corner_size, 0.0),  # Return to origin
        ]
        return profile