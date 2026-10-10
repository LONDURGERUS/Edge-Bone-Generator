# Edge Recessed Bone Generator for Blender

A free, open-source Blender add-on designed for riggers to quickly generate recessed B-Bones along selected mesh edges, perfectly oriented to surface vertex normals.

![Blender Version](https://img.shields.io/badge/Blender-4.0%2B-blue)
![License](https://img.shields.io/badge/License-GPLv3-green)

---

## 🚀 Features

* **Edge-to-Bone Automation:** Select edges in Mesh Edit Mode and generate custom armatures instantly.
* **Vertex Normal Recession:** Automatically offsets bone heads inward along the vertex normal for clean subsurface deformation.
* **Smart Active Vertex Tracking:** Respects your active vertex selection as the starting point (falling back to a $Z$-height sort if no active vertex is set).
* **B-Bone Support:** Automatically sets up B-Bone segments, cross-sectional scale, and roll alignment based on surface normals.
* **Persistent Preferences:** Customize your default settings in the Add-on Preferences so your favorite numbers load every time you open Blender.
* **Non-Destructive Workflow:** Keeps you safely inside Mesh Edit Mode without causing duplication bugs.

---

## 📦 Installation

1. Download the latest release `.py` file (or clone the repository).
2. Open Blender and go to **Edit > Preferences > Add-ons**.
3. Click **Install...** at the top right and select your downloaded script.
4. Enable the checkmark next to **Edge Recessed Bone Generator**.
5. *(Optional)* Expand the add-on preferences to set your permanent default numbers.

---

## 🎮 How to Use

1. Select your mesh object and enter **Edit Mode (`Tab`)**.
2. Select the edge(s) where you want to generate bones. 
   * *Tip:* Click an **Active Vertex** first if you want the bone to specifically start from that vertex.
3. Open the 3D Viewport Sidebar (`N` key) and navigate to the **Rigging** tab.
4. Adjust your settings in the **Edge Bone Generator** panel:
   * **Bone Length:** Controls the length of the generated bones.
   * **BBone Scale:** Sets the cross-sectional width/height.
   * **Inside Offset:** Controls how far inward the bone head sinks along the vertex normal.
   * **B-Bone Segments:** Sets the bending segments for the bones.
   * **Armature:** The name of the target armature object.
5. Click **Create Edge Bones**!

---

## ⚙️ Default Preferences

Want your preferred measurements to load automatically? 
1. Go to **Edit > Preferences > Add-ons**.
2. Search for **Edge Recessed Bone Generator** and expand its panel.
3. Modify your default length, scale, offset, and naming prefix.

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the [LICENSE](LICENSE) file for details.
