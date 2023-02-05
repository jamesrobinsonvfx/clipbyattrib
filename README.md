# Clip by Attribute

# [Get the HDA](https://github.com/jamesrobinsonvfx/clipbyattrib/releases/latest/download/sop_clipbyattrib_1_0.hda)

![Cover Photo](https://github.com/jamesrobinsonvfx/clipbyattrib/blob/main/houdini/help/images/clipbyattrib-cover-resized.jpg)

## Overview
Uses the **Clip SOP** to cut primitives whose user-specified point attribute value is outside a certain threshold.

Using the **Blast SOP** with a group expression is very similar, but since it deletes
points/prims entirely you usually wind up with a steppy, geometric edge.

Since this node uses **Clip SOP** instead, primitives can be cut more accurately
and the result can be a bit nicer. Often pairs well with a **Delta Mush**.

## Viewer State Features

- Click to sample clipping threshold from a mesh
- Use your mouse's scroll wheel* to interactively fine-adjust the clipping threshold
- Clip by a component of a vector attribute
- Hotkeys to cycle vector components, reset clipping threshold, etc.
- Viewport Info Panel HUD
- Help Card

Hit **Enter** in the viewport to enter the [Viewer
State](https://www.sidefx.com/docs/houdini/hom/python_states.html) and check out
the Info Panel HUD for more info about how to use the viewer state features.

> *A little buggy with some mice at the moment, like my Logitech MX Master.

---

All the code is embedded on the node itself (help docs, viewer state, etc) but
I've also got a copy here for easy diffing / reference.

Credit to [Charles Trippe](http://vimeo.com/charlestrippe) for teaching me this
cool method for clipping stuff!
