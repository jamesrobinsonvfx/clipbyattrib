# Clip by Attribute

# [Get the HDA](https://github.com/jamesrobinsonvfx/clipbyattrib/releases/download/latest/sop_clipbyattrib_1_0.hda)

![Cover Photo](https://github.com/jamesrobinsonvfx/clipbyattrib/blob/main/houdini/help/images/clipbyattrib-cover-resized.jpg)

## Overview
Use the Clip SOP to cut primitives whose user-specified attribute value is outside a certain threshold.

Using the [Node:sop/blast] SOP with a group expression is very similar, but since it deletes
points/prims entirely you usually wind up with a steppy, geometric edge.

Since this node uses [Node:sop/clip] instead, primitives can be cut more accurately
and the result can be a bit nicer. Often pairs well with a **Delta Mush**.

## Features

Hit **Enter** in the viewport to enter the [Viewer
State](https://www.sidefx.com/docs/houdini/hom/python_states.html) and check out
the Info Panel HUD for more info about how to use the viewport features.

* Click to sample clipping threshold
* Scroll wheel to interactively fine-adjust the clipping threshold*
* Clip by a vector attribute and hotkeys to cycle through the components
* Info Panel

> *A little buggy with some mice at the moment, like my Logitech MX Master.

---

All the code is embedded on the node itself (help docs, viewer state, etc) but
I've also got a copy here for easy diffing / reference.

Credit to [Charles Trippe](http://vimeo.com/charlestrippe) for teaching me this
cool method for clipping stuff!