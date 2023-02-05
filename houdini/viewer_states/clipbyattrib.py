"""
State:          Clip by Attribute
State type:     clipbyattrib
Description:    Clip geometry above or below a threshold based on a point attribute.
Author:         james
Date Created:   February 05, 2023 - 15:00:00
"""
import hou
import viewerstate.utils as su

from math import floor, log


class State(object):

    KEYMAP = {
        "showguide": "G",
        "reset_clip": "0",
        "keep_above": "A",
        "keep_below": "B",
    }

    # Build HUD Template
    HUD_TEMPLATE = {
        "title": "Clip by Attribute", "desc": "tool", "icon": "SOP_clip",
        "rows": [
            {"id": "attrib", "label": "Attribute",},
            {"id": "comp", "label": "Vector Component", "visible": False,},
            {"id": "clipop", "label": "Keep Mode",},
            {"id": "clip", "label": "Clipping Threshold", "key": "LMB",},
            {"id": "div", "type": "divider", "label": "Hotkeys",},
            {"id": "showguide", "label": "Show Guide Geometry", "key": KEYMAP["showguide"],},
            {"id": "reset_clip", "label": "Reset Clipping Threshold", "key": KEYMAP["reset_clip"],},
            {"id": "keep_above", "label": "Keep Above", "key": KEYMAP["keep_above"],},
            {"id": "keep_below", "label": "Keep Below", "key": KEYMAP["keep_below"],},
            {"id": "switch_comp", "label": "Switch Vector Component", "key": "1-4",},
            {"id": "div", "type": "divider", "label": "Mouse Actions",},
            {"id": "sample_clipping_thresh", "label": "Sample Clipping Threshold", "key": "LMB",},
            {"id": "adjust_clip", "label": "Adjust Clipping Threshold", "key": "mousewheel",},
            {"id": "adjust_clip_fine", "label": "Fine Adjust Clipping Threshold", "key": "SHIFT mousewheel"},
        ]
    }

    LISTEN_PARMS = [
        "attrib",
        "clip",
        "clipop",
        "comp"
    ]

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer

        # Declare some attributes to use throughout the state
        self.node = None
        self.cursor = None
        self.geometry = None

        # Initialize info panel
        self.scene_viewer.hudInfo(hud_template=self.HUD_TEMPLATE)

    def onEnter(self,kwargs):
        """Called on node bound states when it starts."""
        self.node = kwargs["node"]
        self.state_parms = kwargs["state_parms"]

        self.geometry = self.node.node("INPUT_GEO").geometry()

        # Enable / show the cursor
        self.cursor = self.initializeCursor()

        # Show / update the HUD
        self.updateInfoPanel()

        # Add node event callback while the state is active to monitor parms
        if self.node:
            self.node.addEventCallback(
                [hou.nodeEventType.ParmTupleChanged], self.updateParms)

    def onExit(self,kwargs):
        """Called when the state terminates."""
        # Remove node event callback
        if self.node:
            self.node.removeEventCallback(
                [hou.nodeEventType.ParmTupleChanged], self.updateParms)

    def onInterrupt(self, kwargs):
        """Called when the state is interrupted
        e.g when the mouse moves outside the viewport."""
        self.cursor.show(False)

    def onResume(self, kwargs):
        """Called when an interrupted state resumes."""
        # Show the cursor again
        self.cursor.show(True)
        self.updateInfoPanel()

    def onMouseEvent(self, kwargs):
        """Process mouse events."""
        ui_event = kwargs["ui_event"]
        dev = ui_event.device()
        ray = ui_event.ray()

        # Cast a ray into the scene
        hitprim, P, N, uv = su.sopGeometryIntersection(self.geometry, *ray)

        # If we didn't hit the geo, hit the cplane and exit
        if hitprim < 0:
            P = su.cplaneIntersection(self.scene_viewer, *ray)
            self.updateCursor(P, N)
            return
        self.updateCursor(P, N)

        # If the left mouse isn't being pressed, just do an early return
        if not dev.isLeftButton():
            return

        # Query clip attrib name from parameters
        clip_attrib = self.node.evalParm("attrib")
        attrib = self.geometry.findPointAttrib(clip_attrib)
        if not attrib:
            return

        # Sample clip attribute
        clip = self.geometry.prim(hitprim).attribValueAtInterior(attrib, *uv)
        # Determine if it's a vector, and which component to use
        if attrib.size() > 1:
            clip = clip[self.node.evalParm("comp")]

        # Set clipping threshold based on sample
        self.node.parm("clip").set(clip)

        # Must return True to consume the event
        return False

    def onMouseWheelEvent(self, kwargs):
        """Process a mouse wheel event."""
        ui_event = kwargs["ui_event"]

        # Clipping threshold parameter on our node
        clip_parm = self.node.parm("clip")

        # TODO: Handle weird mice like my Logitech MX Master
        # Some mice can scroll in some sort of crazy turbo mode
        # But also really weakly (>0 <1)
        scroll_amount = ui_event.device().mouseWheel()
        # self.log(f"Raw Scroll: {scroll_amount}")
        scroll_amount = min(1, max(-1, round(scroll_amount)))
        # self.log(f"Clamped Scroll: {scroll_amount}")

        # Determine increment based on current threshold's order of magnitude
        threshold_mag = self.orderOfMagnitude(clip_parm.eval())
        increment = self.mouseWheelIncrement(threshold_mag) # coarse

        # Fine scrubbing if Shift key is pressed
        if ui_event.device().isShiftKey():
            increment = self.mouseWheelIncrement(threshold_mag - 1)

        # Update the clipping parameter
        clip_parm.set(clip_parm.eval() + scroll_amount * increment)

        # Must return True to consume the event
        return False

    def onMenuPreOpen(self, kwargs):
        """Update the menu content before it is drawn."""
        menu_states = kwargs["menu_states"]
        menu_item_states = kwargs["menu_item_states"]

        # Match to parameter states on the node
        # Guide geo
        if kwargs["menu"] == "clipbyattrib_menu":
            # self.log(menu_item_states)
            menu_item_states["showguide"]["value"] = self.node.evalParm("showguide")

        # Keep Mode
        if kwargs["menu"] == "rstrip_clipop":
            menu_states["value"] = "rb_" + self.node.parm("clipop").evalAsString()

        # Vector component, if needed
        if kwargs["menu"] == "rstrip_comp":
            is_vector = self.node.evalParm("attribsize") > 1
            comp_parm = self.node.parm("comp")
            # Disable components if they aren't available
            for comp in menu_item_states.keys():
                enable = comp in comp_parm.menuItems()
                for _ in ["enable", "visible"]:
                    menu_item_states[comp][_] = is_vector and enable
            # Set to the currently selected component on the node
            if is_vector:
                menu_states["value"] = comp_parm.menuItems()[self.node.evalParm("comp")]

    def onMenuAction(self, kwargs):
        """Called when a menu item has been selected."""
        menu_item = kwargs["menu_item"]

        # Toggle guide geometry
        if menu_item == "showguide":
            self.node.parm("showguide").set(not self.node.evalParm("showguide"))
        # Reset clipping threshold
        elif menu_item == "reset_clip":
            self.node.parm("clip").revertToDefaults()
        # Set the Keep Mode
        elif menu_item == "rstrip_clipop":
            menu_parm = self.node.parm("clipop")
            menu_parm.set(
                menu_parm.menuItems().index(kwargs["rstrip_clipop"][3:]))
        # Set the vector component
        elif menu_item == "rstrip_comp":
            comp_parm = self.node.parm("comp")
            # Only set if it's enabled (can still use hotkey when disabled)
            try:
                comp_parm.set(comp_parm.menuItems().index(kwargs["rstrip_comp"]))
            except (IndexError, ValueError):
                pass
            self.updateInfoPanel()

    def initializeCursor(self):
        """Create a drawable to use in the viewport."""
        geo = hou.Geometry()

        # Make a cone
        tube_verb = hou.sopNodeTypeCategory().nodeVerb("tube")
        tube_verb.setParms({"orient": 2, "rad": (0.01, 0.5), "t": (0, 0, -0.5)})
        tube_verb.execute(geo, [])

        # Create a drawable
        drawable = hou.SimpleDrawable(
            self.scene_viewer, geo, self.state_name + "_cursor")
        drawable.setWireframeColor(hou.Color(1, 0, 0))
        drawable.enable(True)
        drawable.show(True)
        return drawable

    def updateCursor(self, P, N):
        """Update the cursor location in the viewport."""
        parent = su.ancestorObject(self.node)
        parent_xform = parent.worldTransform()
        rot = hou.Vector3(0, 0, -1).matrixToRotateTo(N)
        xform = hou.hmath.buildScale(hou.Vector3(0.1, 0.1, 0.1))
        xform *= hou.hmath.buildRotate(rot.extractRotates())
        xform *= hou.hmath.buildTranslate(P)
        xform *= parent_xform
        self.cursor.setTransform(xform)

    def updateInfoPanel(self):
        """Update the info panel when parms change."""
        updates = {}
        for parm_name in self.LISTEN_PARMS:
            parm = self.node.parm(parm_name)
            value = ""
            if isinstance(parm.parmTemplate(), hou.FloatParmTemplate):
                value = parm.evalAsFloat()
                pad = 3 if value else 0 # Don't pad if it's just zero
                value = f"{parm.evalAsFloat():.{pad}f}"
            else:
                value = self.node.parm(parm_name).evalAsString()
            updates[parm_name] = value

        # Attribute
        attrib = self.node.evalParm("attrib")
        if self.node.evalParm("attribsize") > 1:
            comp_parm = self.node.parm("comp")
            updates["attrib"] = f"{attrib}.{comp_parm.menuItems()[comp_parm.eval()]}"

        # Component
        # TODO: Broken in h19
        if hou.applicationVersion()[0] >= 19 and hou.applicationVersion()[1] >= 5:
            updates["switch_comp"] = {"visible": self.node.evalParm("attribsize") > 1} # TODO: This doesn't seem consistent. Bug?

        self.scene_viewer.hudInfo(hud_values=updates)
        self.scene_viewer.hudInfo(show=True)

    def updateParms(self, **kwargs):
        """Callback to add to node for listening to parm changes."""
        # Since we named the info panel ids after our parms, it should be easy
        # to link up to a callback to listen for changes and force an update
        parm = kwargs["parm_tuple"]
        if parm.name() in self.LISTEN_PARMS:
            # Do stuff when parms update
            self.updateInfoPanel()

    @staticmethod
    def orderOfMagnitude(value) -> int:
        """Find the order of magnitude of a number."""
        value = value if value else 0.1 # Avoid passing 0 to log()
        return floor(log(abs(value), 10))

    @staticmethod
    def mouseWheelIncrement(magnitude) -> float:
        """Convert order of magnitude to scale scroll amount by."""
        return pow(10, magnitude)


def createViewerStateTemplate():
    """Mandatory entry point to create and return the viewer state
    template to register.
    """

    state_typename = "clipbyattrib.pystate"
    state_label = "Clip by Attribute"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)
    template.bindIcon("SOP_clip")

    # Create and bind context menu
    menu = hou.ViewerStateMenu("clipbyattrib_menu", "Clip by Attribute")
    hkey = su.hotkey(state_typename, "showguide", State.KEYMAP["showguide"], "Show Guide Geometry")
    menu.addToggleItem("showguide", "Show Guide Geometry", False, hotkey=hkey)
    hkey = su.hotkey(state_typename, "reset_clip", State.KEYMAP["reset_clip"], "Reset Clipping Threshold")
    menu.addActionItem("reset_clip", "Reset Clipping Threshold", hotkey=hkey)

    # Keep Mode Radio Strip
    menu.addRadioStrip("rstrip_clipop", "Keep", "rb_above")
    hkey = su.hotkey(state_typename, "keep_above", State.KEYMAP["keep_above"], "Keep Above")
    menu.addRadioStripItem("rstrip_clipop", "rb_above", "Above", hkey)
    hkey = su.hotkey(state_typename, "keep_below", State.KEYMAP["keep_below"], "Keep Below")
    menu.addRadioStripItem("rstrip_clipop", "rb_below", "Below", hkey)

    # Vector Component Radio Strip
    menu.addRadioStrip("rstrip_comp", "Component", "x")
    hkey = su.hotkey(state_typename, "comp_x", "1", "Use X Component")
    menu.addRadioStripItem("rstrip_comp", "x", "X", hkey)
    hkey = su.hotkey(state_typename, "comp_y", "2", "Use Y Component")
    menu.addRadioStripItem("rstrip_comp", "y", "Y", hkey)
    hkey = su.hotkey(state_typename, "comp_z", "3", "Use Z Component")
    menu.addRadioStripItem("rstrip_comp", "z", "Z", hkey)
    hkey = su.hotkey(state_typename, "comp_w", "4", "Use W Component")
    menu.addRadioStripItem("rstrip_comp", "w", "W", hkey)

    template.bindMenu(menu)

    return template
