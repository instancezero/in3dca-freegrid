# In3D.ca FreeGrid Storage System

This project contains [FreeCAD](https://freecadweb.org) macros for generating FreeGrid storage system components.

## Installation

Clone or download the project, copy the contents of the FreeCAD-Macros folder into your FreeCAD user macro folder.
If you update the code, restarting FreeCAD is advised.

## Community/Contributing

If you use FreeGrid or add components to it, please let me know!

You can find In3D:

* on the web at [In3D.ca](https://in3d.ca)
* at [Cults3D](https://cults3d.com/en/users/In3d/creations)
* as @in3dca on [Instagram](https://www.instagram.com/in3dca/) and [Twitter](https://twitter.com/in3dca)
* on [Facebook](https://www.facebook.com/in3dca)

Bug reports, coding questions, and pull requests are welcome on Github.

## History

This project was initially inspired by [Alexandre Chappel's](https://www.youtube.com/watch?v=OsLc76k4KeM) workshop
organization system. But I wanted to design some of my own components and there were no CAD files available.

So I started working on my own, but like many projects it got shuffled aside. Then I got a CNC router and
my limited workspace turned into an unmanageable mess. I thought I'd do another search before returning to my project
and found Zack Freedman's [Gridfinity system](https://www.youtube.com/watch?v=ra_9zU-mnl8). Perfect, here's a free
system that saves be going back to my design from scratch approach!

Alas, nothing is perfect. So here's my "more perfect for me" alternative. I hope others will find it worthwhile.

## A Digression: 3D Printing and CAD

The 3D printing community has a love affair with Autodesk's Fusion 360. After all, it's free, why not?

But Fusion is only free as in "no cost for limited use", not free as in freedom. While Fusion 360 is more powerful than
FreeCAD for most of what I do, there aren't enough advantages to prefer it. Also, I'm a software developer:
"parametric" CAD systems are great, but my concept of parameters is higher level. It's great that you can go into
different shapes to adjust and change a design, but when those parameters are deeply nested, this is
still a tricky process. For me, a parameter is something you supply to a block of code to get the object you want;
the underlying code should be responsible for working out the details. FreeCAD's macros give me the capability of doing
just that. Fusion 360 doesn't even come close.

## Back to "not quite perfect"

Gridfinity looks great. Actually it's fantastic. There's a rule for ADD people that if something is out of
sight, it ceases to exist. Zach's system really helps with this problem: most of his components keep things visible
while still keeping them organized. His glass-front modules are inspired. I'll probably make a version of those soon.
It's also totally free. It's really taken off and that's good for pretty much everyone.

I enthusiastically printed out a few of his modules and ran into some things I wasn't really happy with:

* He uses Fusion 360. Importing his work wasn't possible, unless I just wanted a bunch of primitives.
  This means no parameters at all and that's essentially useless.
* His grid size is 42mm, which seems odd. I think he picked it so his grids would fit perfectly in his shop drawers.
  In my case, I've got big hands and getting two fingers into a 1x1 box to fish out a small part simply doesn't work
  that well.
* The default boxes come in a 24mm height. The system I was working on used multiples of 10mm. I am more
  comfortable with that. Also, anything in the range of 25mm feels like an inch. Eeew.

All this inspired me to take another look at my system. As it turns out, it was most of the way there. It uses a
50mm grid, 10mm unit height. The design is slightly more angular but I kind of prefer that anyway.

What was missing is something that made it easy for non-programmers to generate components. So I added a user interface,
cleaned the code up, and made it available to everyone. I hope to add more "standard" objects to the system, but with
basic resizeable grids and boxes, it's already got a lot of flexibility: generate a core box and then customize to fit
your needs.

## Individual Components

The option "Generate components as individual shapes" will create a box with dividers, the front "scoop" and the label
area all as separate FreeCAD shapes. By default, dividers split the inside of the box evenly, but what if you want a
different allocation of space? Simple: use the individual components feature, then reposition the dividers, and form a
union to get the custom box you need.

## Generating and Printing

The bigger the grid/box, the more complex the computations. Generating a 5x5 grid with magnets can take a few seconds,
depending on the speed of your system. Be patient.

Boxes have hollow bottoms, and need to be printed with supports. Prusa Slicer's "paint on" supports are great for
getting the bottoms supported without generating needless supports around the outside.

Longer parts can be subject to warping, so good bed adhesion is critical. A while back I switched to a PEI coated
flexible steel bed. I can't say enough good things about that choice. Well worth the cost in saved time, tape, glue,
failed prints, and frustration.

As of version 1.0, the base grids have a little corner detail that was designed to make it possible to add a coupling
and link grids together more securely. The current design is too detailed to be useful and a better version is on
the way. Your slicer might want to add supports there, but it's not necessary.