# Clip by Attribute

# [Get the HDA](https://github.com/jamesrobinsonvfx/clipbyattrib/releases/latest/download/sop_clipbyattrib_1_0.hda)

![Cover Photo](https://github.com/jamesrobinsonvfx/clipbyattrib/blob/main/houdini/help/images/clipbyattrib-cover-resized.jpg)

## Overview

This node uses the **Clip SOP** to cut primitives whose user-specified point attribute value is
outside a certain threshold. It's one of my favorite little tools, and I really wanted
to explore creating [Viewer
States](https://www.sidefx.com/docs/houdini/hom/python_states.html) in Houdini. I'm by ***no
means*** a Python Viewer State expert, so keep that in
mind when you're poking around the code ;)


---

Using the **Blast Sop** with a group expression is very similar, but since it
deletes points/prims entirely, you usually wind up with a steppy, geometric
edge.

Single this node uses the **Clip SOP** instead, primitives can be cut more
accurately and the result can be a bit nicer. Often pairs well with a **Delta
Mush**

[![Blast SOP]({{ images }}/compare-blast.png){:height="100%" width="100%"}]({{
images }}/compare-blast.png)
*Blast SOP. A bit jaggy.*

[![Clip by Attribute]({{ images }}/compare-clipbyattrib.png){:height="100%" width="100%"}]({{ images }}/compare-clipbyattrib.png)
*Clip by Attribute. Much smoother!*

---

All the code is embedded on the node itself (help docs, viewer state, etc) but I've also got a copy in the repo for easy diffing / reference.

## Viewer State Features

[![Viewer State Info Panel]({{ images }}/viewer-state-info-panel.png){:height="100%" width="100%"}]({{ images }}/viewer-state-info-panel.png)

- Click to sample clipping threshold from a mesh
- Use your mouse's scroll wheel* to interactively fine-adjust the clipping threshold
- Clip by a component of a vector attribute
- Hotkeys to cycle vector components, reset clipping threshold, etc.
- Viewport Info Panel HUD
- Help Card

Hit **Enter** in the viewport to enter the [Viewer
State](https://www.sidefx.com/docs/houdini/hom/python_states.html) and check out
the **Info Panel HUD** for more info about how to use the viewer state features.

> *A little buggy with some mice at the moment, like my Logitech MX Master

---

Credit to [Charles Trippe](http://vimeo.com/charlestrippe) for teaching me this cool method for clipping stuff!
