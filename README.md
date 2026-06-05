# Modeling_Publisher_maya
### Modeling publisher that uses the principles of CVEI with discord push notifications for enforcing publishing standards in production.
A publisher tool to verify the model's integrity, file naming conventions, and model qualities (e.g., ngons or lamina-faced elements) before exporting to look development.

# Demo Videos:
Click to see the Demo:

[![Watch the project demo](modeling_publisher_maya/docs/ui.png)](https://vimeo.com/1198895814?share=copy&fl=sv&fe=ci)

# Current Features (V.1.0.0):
### Geometry Validation
* Checks naming convention on file.
* Checks naming convention on asset.
* Checks for Ngons, and manifold geometry.
* It publishes to the project destination in the script.
* Notifies discord server using the bot in the enviroment vartiables.

# How to install:

### Method 1: Standard Installation (Recommended for Artists)

**1. Download the Package**
* Click the green **Code** button and select **Download ZIP**.
* Extract the contents of the ZIP file to a location on your computer.

**2. Copy to your Maya Scripts Folder**
* Open your local Maya scripts directory. By default, this is located at:
  * **Windows:** `C:\Users\<YourUsername>\Documents\maya\<maya_version>\scripts`
  * **Mac:** `~/Library/Preferences/Autodesk/maya/<maya_version>/scripts`
  * **Linux:** `~/maya/<maya_version>/scripts`
* Copy the `environment_exporter` folder from the extracted ZIP and paste it directly into your Maya `scripts` folder.
  
**3. Launch the Tool in Maya**
* Open Autodesk Maya.
* Open the **Script Editor** (`Windows > General Editors > Script Editor`).
* Create a new **Python** tab and paste the following execution code:

  ```python
  import publish_UI
  publish_UI.main()

# Requirements:
* Maya 2022+
* Enviroment variable with discord bot named "PIPELINE_DISCORD_BOT"


# Quick Start:
### First time setup.
Make sure that you have the right plugins enabled in Unreal Engine and that the Maya you are working is newer than Maya 2022+

### Basic Workflow.
* Select the mesh you want and follow along with the publishing rules.
* The preset naming convention is a 3_ name space for the scene (scene_artist_v01) any three scene structure, and for the assets is geo_{asset}_{type}_{subtype}
* After that it will check the status of your geometry before export.

It will automatically open your project and import the meshes if the right plug ins are enabled.

# Current Limitations:
* Change your project settings for verifications you have to do it in the script.
* It only works if you have the discord bot in your enviroment variables.
* It only handles modeling department for publishing.
  
# File Reference:
### Maya Scripts:
* <u>publish_UI.py</u> It navigates the Pyside logic and UI.
* <u>publish.py</u> It handles the veirification logic.

# The Problem
I am not a good modeler and often make mistakes in my models that eventually come back to haunt me during my texturing or rigging phase. 
Using my Python skills, I attempted to build a production-level publishing tool that ensures our models are optimized for the next stages of our 3D development.  

# The Solution
The first stage was to build the class system with the different steps and the basic functions, in case I want to further develop this tool into multiple departments, such as lighting or rigging. 
 
For the modeling tool, I used class inheritance to build the specific functions I needed for my object to verify the specific problems a 3d model might have in production. I built a UV checker, an ngon checker, lamina faces, and of course, checked the naming convention. 

In the extraction face, it exports the model as either an OBJ or FBX to the assets folder in the standard Maya project folder  structure. I stored the published information in a CSV to later transfer into an Excel, Google Sheet, or production tracking software like ShotGrid. 

My most exciting integration was the use of enviroment variables to store and access my production Discord bot link to send a notification when I publish a model into my respective Discord channel.



