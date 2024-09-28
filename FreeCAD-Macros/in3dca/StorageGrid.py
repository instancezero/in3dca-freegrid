#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate In3D.ca FreeGrid storage grid components in FreeCAD.

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

__Name__ = "In3D.ca FreeGrid Storage System Grid"
__Comment__ = "Generate In3D.ca FreeGrid storage grids"
__Author__ = "Alan Langford <prints@in3d.ca>"
__Version__ = "See CHANGELOG"
__Date__ = ""
__License__ = "GNU AGPLv3+"
__Web__ = "https://in3d.ca"
__Wiki__ = ""
__Icon__ = ""
__Help__ = ""
__Status__ = ""
__Requires__ = ""
__Communication__ = ""
__Files__ = ""

import Part
from FreeCAD import Base, Placement, Rotation
from freecad.freegrid.in3dca import h


class StorageGrid:
    """Class to manage the geometry of the Storage Grid."""

    def __init__(self):
        """Initialize the attributes of the StorageGrid object."""
        self.reset()

    def connector_insert(self) -> Part.Solid:
        """Create a hole to accommodate the connectors, counter-clockwise."""
        profile = [
            h.xyz(-0.1, -0.1),  # Start outside origin
            h.xyz(2.5, -0.1),  # Trim off sharp corner edge
            h.xyz(2.5, 0.5),  # cut into corner
            h.xyz(3.2, 1.2),  # Diagonal up arm
            h.xyz(4.4, 1.2),  # Bottom of tab
            h.xyz(4.4, 2.3),  # Outer corner of tab
            h.xyz(2.3, 2.3),  # Acute center vertex
            h.xyz(2.3, 4.4),  # Outer corner of tab
            h.xyz(1.2, 4.4),  # Inner corner, upper wing
            h.xyz(1.2, 3.2),  # Back to diagonal
            h.xyz(0.5, 2.5),  # Diagonal back out
            h.xyz(-0.1, 2.5),  # Cut the corner
            h.xyz(-0.1, -0.1),  # close the polygon
        ]
        face = Part.Face(Part.makePolygon(profile))
        insert = face.extrude(h.xyz(z=1.95 + self.extra_bottom))
        insert.Placement = Placement(h.xyz(z=-0.05 - self.extra_bottom), Rotation())
        return insert

    def inner_rail_profile(self) -> list[Base.Vector]:
        """Create the profile used on the inner rails."""
        half = self.rail_width / 2.0
        half_top = self.top_width / 2.0
        lift = self.magnet_floor_thickness
        # counter-clockwise from left bottom bevel
        profile = [
            h.xyz(-(half - self.bevel - self.clearance), z=0.0),
            # Across the bottom
            h.xyz(half - self.bevel - self.clearance, z=0.0),
            # Right lower bevel
            h.xyz(half - self.clearance, z=self.bevel),
            # Right vertical edge
            h.xyz(half - self.clearance, z=1.0 + lift),
            # 45 degrees to the top
            h.xyz(half_top, z=self.rail_height - self.clearance + lift),
            # Top face
            h.xyz(-half_top, z=self.rail_height - self.clearance + lift),
            # 45 degrees to the left vertical edge
            h.xyz(-(half - self.clearance), z=1.0 + lift),
            # Left vertical edge
            h.xyz(-(half - self.clearance), z=self.bevel),
            # Left lower bevel back to the start
            h.xyz(-(half - self.bevel - self.clearance), z=0.0),
        ]
        return profile

    def magnet_holder(self, mag_diameter: float, mag_height: float) -> Part.Shape:
        """
        Creates a single corner magnet holder.
        The maximum height of this body is 3.2[mm] meaning that:
        the height of the magnet plus the height of the floor in which
        the magnet is glued sums 3.2mm.
        floor_thickness + mag_diameter = 3.2[mm]

        The initial (arbitrary) square holder size is 13.4[mm], i.e.
        2 * peg_radius + extra = 13.4mm

        As of the current constants:
        - the maximum magnet diameter is 10[mm], 11[mm] don't fit
        - the maximum magnet height is 3[mm] (and 0.2[mm] of floor)
        """
        height = mag_height + 0.2  # Height of the magnet cutter
        mag_radius = mag_diameter / 2.0
        peg_radius = mag_radius + 1.2
        floor_thickness = 3.2 - mag_height
        extra = 13.4 - 2 * peg_radius
        holder = h.poly_to_face(
            [
                h.xyz(),
                h.xyz(peg_radius, 0),
                h.xyz(peg_radius, -peg_radius - extra),
                h.xyz(-peg_radius - extra, -peg_radius - extra),
                h.xyz(-peg_radius - extra, peg_radius),
                h.xyz(0, peg_radius),
                h.xyz(),
            ]
        ).extrude(h.xyz(z=2.4))
        holder = holder.fuse(h.disk(mag_radius + 1.2, self.magnet_floor_thickness))
        holder = holder.cut(h.disk(mag_radius + 0.1, height, h.xyz(z=floor_thickness)))
        return holder

    def make(
        self, x: int = 1, y: int = 1, mag_d: float = 6, mag_h: float = 2, extra_bottom: float = 0
    ) -> Part.Shape:
        """Return the body of a grid including some default values, for testing."""
        self.x_size = x
        self.y_size = y
        self.mag_diameter = mag_d
        self.mag_height = mag_h
        self.extra_bottom = extra_bottom
        outer = self.rails()
        return outer.removeSplitter()

    def outer_rail_profile(self) -> list[Base.Vector]:
        """Create the profile used on the outer rails."""
        half_top = self.top_width / 2.0
        lift = self.magnet_floor_thickness
        # counter-clockwise from inside the bevel on the outer edge
        profile = [
            h.xyz(self.gap + self.bevel, z=0.0),
            h.xyz(2.5 - self.bevel - self.clearance, z=0.0),  # across the bottom
            h.xyz(2.5 - self.clearance, z=self.bevel),  # up the inside bevel
            h.xyz(2.5 - self.clearance, z=1.0 + lift),  # Inside vertical edge
            h.xyz(
                half_top, z=self.rail_height - self.clearance + lift
            ),  # 45 degrees to the top face
            h.xyz(0.1, z=self.rail_height - self.clearance + lift),  # The top face
            h.xyz(0.1, z=0.5),  # Outside vertical edge
            h.xyz(0.6, z=0.0),  # inside bevel to the start point
        ]
        return profile

    def outer_rail_cleanup_face(self) -> Part.Face:
        """Create a face used to clean the corners."""
        profile = [
            h.xyz(0, z=self.bevel + self.gap),
            h.xyz(0, z=0),
            h.xyz(self.bevel + self.gap, z=0),
            h.xyz(0, z=self.bevel + self.gap),
        ]
        return Part.Face(Part.makePolygon(profile))

    def outer_rail_cleanup(self, len: float) -> Part.Solid:
        """Create a solid to clean an artifact left on the corners."""
        face = self.outer_rail_cleanup_face()
        cleanup = face.extrude(h.xyz(y=len))
        return cleanup

    def rails(self) -> Part.Shape:
        """
        Create the grid shape

        Method:
        - Get the profile
        - Extrude
        - Transform to XZ plane
        - Translate to start point (shift and rotate)
        - Repeat for 3 remaining sides.
        """
        rail_length_x = self.x_size * self.spacing - 2 * self.gap
        rail_length_y = self.y_size * self.spacing - 2 * self.gap
        # Left rail
        face = Part.Face(Part.makePolygon(self.outer_rail_profile()))
        rails = face.extrude(h.xyz(y=rail_length_y))
        rails.Placement = Placement(h.xyz(y=0.1), Rotation())

        # Right rail
        new_rail = face.extrude(h.xyz(y=rail_length_y))
        new_rail.Placement = Placement(
            h.xyz(rail_length_x + 2 * self.gap, rail_length_y + self.gap),
            Rotation(h.xyz(z=1.0), 180),
        )
        rails = rails.fuse(new_rail)

        # Bottom rail
        new_rail = face.extrude(h.xyz(y=rail_length_x))
        new_rail.Placement = Placement(h.xyz(rail_length_x + self.gap), Rotation(h.xyz(z=1.0), 90))
        rails = rails.fuse(new_rail)

        # Top rail
        new_rail = face.extrude(h.xyz(y=rail_length_x))
        new_rail.Placement = Placement(
            h.xyz(self.gap, rail_length_y + 2 * self.gap), Rotation(h.xyz(z=1.0), -90)
        )
        rails = rails.fuse(new_rail)

        # Shorten inside rails so that they miss the bottom bevels
        rail_length_x = self.x_size * self.spacing - 1.2
        rail_length_y = self.y_size * self.spacing - 1.2

        # Vertical Rails
        face = Part.Face(Part.makePolygon(self.inner_rail_profile()))
        for slot in range(1, self.x_size):
            new_rail = face.extrude(h.xyz(y=rail_length_y))
            new_rail.Placement = Placement(h.xyz(slot * self.spacing, 0.6), Rotation())
            rails = rails.fuse(new_rail)

        # Horizontal Rails
        for slot in range(1, self.y_size):
            new_rail = face.extrude(h.xyz(y=rail_length_x))
            new_rail.Placement = Placement(
                h.xyz(rail_length_x + 0.6, slot * self.spacing), Rotation(h.xyz(z=1.0), 90)
            )
            rails = rails.fuse(new_rail)

        # Extra material under the grid, to simulate a thick wood piece
        if self.is_subtractive:
            base = h.poly_to_face(
                [
                    h.xyz(self.gap, self.gap, -self.extra_bottom),
                    h.xyz(self.spacing * self.x_size - 2 * self.gap, 0, -self.extra_bottom),
                    h.xyz(
                        self.spacing * self.x_size - 2 * self.gap,
                        self.spacing * self.y_size - 2 * self.gap,
                        -self.extra_bottom,
                    ),
                    h.xyz(0, self.spacing * self.y_size - 2 * self.gap, -self.extra_bottom),
                    h.xyz(self.gap, self.gap, -self.extra_bottom),
                ]
            ).extrude(h.xyz(z=self.extra_bottom + 2.4 + 0.8))
            # Part.show(base, 'base')
            rails = rails.fuse(base)

            # Magnet holders on subtractive mode
            if self.magnets:
                magnet_hole = h.disk(self.mag_diameter / 2 + 0.1, 2.4 + 0.8, h.xyz(z=1.2))
                c = 10 - (self.mag_diameter - 6) / 2.0
                for i in range(0, self.y_size):
                    y = i * self.spacing
                    for w in range(0, self.x_size):
                        x = w * self.spacing
                        magnet_hole.Placement = Placement(h.xyz(x + c, y + c), Rotation())
                        rails = rails.cut(magnet_hole)
                        magnet_hole.Placement = Placement(
                            h.xyz(x + self.spacing - c, y + c), Rotation(h.xyz(z=1), 90)
                        )
                        rails = rails.cut(magnet_hole)
                        magnet_hole.Placement = Placement(
                            h.xyz(x + c, y + self.spacing - c), Rotation(h.xyz(z=1), 270)
                        )
                        rails = rails.cut(magnet_hole)
                        magnet_hole.Placement = Placement(
                            h.xyz(x + self.spacing - c, y + self.spacing - c),
                            Rotation(h.xyz(z=1), 180),
                        )
                        rails = rails.cut(magnet_hole)

        else:
            # NOTE: Magnet holders on additive mode (original)
            # Apparently the distance from the holder to the immediate grid border is 14.1[mm]
            # The diameter of the magnet and the constant 'c' play a role here
            # The holder separates from the grid border: (mag_diameter - 6mm)/2
            if self.magnets:
                holder = self.magnet_holder(self.mag_diameter, self.mag_height)
                c = 10 - (self.mag_diameter - 6) / 2.0
                for i in range(0, self.y_size):
                    y = i * self.spacing
                    for w in range(0, self.x_size):
                        x = w * self.spacing
                        holder.Placement = Placement(h.xyz(x + c, y + c), Rotation())
                        rails = rails.fuse(holder)
                        holder.Placement = Placement(
                            h.xyz(x + self.spacing - c, y + c), Rotation(h.xyz(z=1), 90)
                        )
                        rails = rails.fuse(holder)
                        holder.Placement = Placement(
                            h.xyz(x + c, y + self.spacing - c), Rotation(h.xyz(z=1), 270)
                        )
                        rails = rails.fuse(holder)
                        holder.Placement = Placement(
                            h.xyz(x + self.spacing - c, y + self.spacing - c),
                            Rotation(h.xyz(z=1), 180),
                        )
                        rails = rails.fuse(holder)

        if self.corner_connectors:
            # Cut spaces for the connectors
            zz = -0.05 - self.extra_bottom
            insert = self.connector_insert()
            insert.Placement = Placement(h.xyz(z=zz), Rotation())
            rails = rails.cut(insert)
            insert.Placement = Placement(
                h.xyz(self.x_size * self.spacing, 0, zz), Rotation(h.xyz(z=1.0), 90)
            )
            rails = rails.cut(insert)
            insert.Placement = Placement(
                h.xyz(self.x_size * self.spacing, self.y_size * self.spacing, zz),
                Rotation(h.xyz(z=1.0), 180),
            )
            rails = rails.cut(insert)
            insert.Placement = Placement(
                h.xyz(0, self.y_size * self.spacing, zz), Rotation(h.xyz(z=1.0), 270)
            )
            rails = rails.cut(insert)
        else:
            x_len = self.x_size * self.spacing
            y_len = self.y_size * self.spacing
            cleanup_x = self.outer_rail_cleanup(y_len)  # x face is y len long
            cleanup_y = self.outer_rail_cleanup(x_len)  # y face is x len long

            cleanup_x.Placement = Placement(h.xyz(), Rotation(h.xyz(z=1.0), 0))
            rails = rails.cut(cleanup_x)

            cleanup_x.Placement = Placement(
                h.xyz(x_len, self.y_size * self.spacing - self.gap), Rotation(h.xyz(z=1.0), 180)
            )
            rails = rails.cut(cleanup_x)

            cleanup_y.Placement = Placement(h.xyz(x_len), Rotation(h.xyz(z=1.0), 90))
            rails = rails.cut(cleanup_y)

            cleanup_y.Placement = Placement(h.xyz(y=y_len), Rotation(h.xyz(z=1.0), -90))
            rails = rails.cut(cleanup_y)
        return rails

    def reset(self):
        """Reset the attributes of the StorageGrid object to their default values."""
        self.bevel = 0.5
        self.clearance = 0.3
        self.gap = 0.1
        self.magnet_floor_thickness = 2.0 + 1.2
        self.magnets = True
        self.spacing = 50
        self.rail_height = 3.0
        self.rail_width = 5.0
        self.top_width = 1.0
        self.x_size = 3
        self.y_size = 3
        self.mag_diameter = 6
        self.mag_height = 2
        self.corner_connectors = True
        self.is_subtractive = False
        self.extra_bottom = 0

    def self_test(self):
        """Generate test grids."""
        start = h.xyz(z=-60)
        incr = 60

        self.reset()
        g1x1 = self.make(1, 1)
        g1x1.Placement = Placement(start, Rotation())
        Part.show(g1x1, "g1x1")
        start.x += incr

        self.reset()
        self.magnets = False
        g1x1_nm = self.make(1, 1)
        g1x1_nm.Placement = Placement(start, Rotation())
        Part.show(g1x1_nm, "g1x1_nm")
        start.x += incr

        self.reset()
        g1x2 = self.make(1, 2)
        g1x2.Placement = Placement(start, Rotation())
        Part.show(g1x2, "g1x2")
        start.x += incr

        self.reset()
        g2x1 = self.make(2, 1)
        g2x1.Placement = Placement(start, Rotation())
        Part.show(g2x1, "g2x1")
        start.x += 2 * incr

    def set_param(self, name: str, value):
        """Convenience method to facilitate data-driven generation."""
        # Set to make magnet holes
        if name == "magnets":
            self.magnets = value
        if name == "corner_connectors":
            self.corner_connectors = value
        if name == "is_subtractive":
            self.is_subtractive = value
