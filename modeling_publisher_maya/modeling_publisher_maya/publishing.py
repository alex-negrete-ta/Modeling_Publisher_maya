import getpass
import json
import maya.cmds as cmds
import os
import pathlib
import requests
import datetime
import uuid


class MyPublisher:
    def __init__(self, selection, shotgrid_api, prefix="geo"):
        """
        Description:
        Initialize the Publisher base class.

        Input:
        selection (obj): Maya selection of the export.
        shotgrid_api(str): The API link to shotgrid.

        Output:
        None
        """
        # Establishes the selection.
        self.sel = selection
        self.publish_api = shotgrid_api
        self.prefix = prefix
        self.obj_path = ""

    def main(self):
        """
        Description:
        Executes the main steps of the publishing tool.

        Input:
        None

        Output:
        Bool: True if the export is successful. Raises PublishError if it fails.
        """
        #  Start the logic
        print(" -- Starting publsihing--")

        # Run the logic and raise any errors if any.
        try:
            self.collect_assets()
            self.verify_assets(self.prefix)
            self.extract_assets()
            self.implement_assets()

            cmds.inViewMessage(
                amg="Published Successfully!", pos="midCenter", fade=True
            )
            print("Succesfully exported.")
            return True

        # Publish the error raise.
        except PublishError as e:
            print(f"Published failed: {e}")
            cmds.warning(f"Publish failed: {e}")
            raise e

        except Exception as e:
            print(f"Critical Error: {e}")
            cmds.warning(f"Critical Error: {e}")
            raise e

    def collect_assets(self):
        """
        Description:
        Collects all the assets from the maya selection.

        Input:
        None

        Output:
        True/PublishError (Bool): Either pass as true or raises the error of no selection.
        self.scene (str): Name of the file selection.
        """
        # Verifies the selection is correct.
        if not self.sel:
            raise PublishError("No selections founded.")

        # Collects the scene name.
        name = cmds.file(query=True, exn=True)
        self.scene = name.split("/")[-1]

        print(f"-- Collecting Done {self.scene}--")
        return True

    def verify_assets(self, prefix):
        """
        Description:
        Verifies the naming convention and checks it has the appropiate structure.

        Input:
        None

        Output:
        True/PublishError (Bool): Either pass as true or raises the error of wrong naming.
        """
        # Makes an empty list and sets the naming convention spaces.
        wrong_names = []
        length = [3, 4]

        # Checks the length of the file scene name.
        scene_length = self.scene.split("_")
        if len(scene_length) not in length:
            raise PublishError(
                f"Wrong naming convention for your file name {self.scene}"
            )

        # Verifies spaces for each name.
        for obj in self.sel:
            node_name = obj.split("|")[-1]
            parts = node_name.split("_")

            # It appends it to wrong names for each object.
            if len(parts) not in length:
                wrong_names.append(obj)

            # Verifies the preffix is in the selections.
            if parts[0] != prefix:
                wrong_names.append(obj)

        # It raises the error.
        if wrong_names:
            raise PublishError(f"Naming standard is not right for: {wrong_names}")
        return True

    def extract_assets(self):
        """
        Description: Initializes the extract_assets module as a base class.
        Input: None
        Output: None
        """
        # Extracts and exports the assets
        pass

    def implement_assets(self):
        """
        Description: Initializes the implement_assets module as a base class.
        Input: None
        Output: None
        """
        # Publishes the path in shotgrid.
        pass

    def discord_notification(self, asset_name, version, department, bot_url):
        """
        Description:
        Publishes a message to the Discord bot using enviroment variables.

        Input:
        asset_name (str): Name of the published asset.
        version (int): Version number of the published asset.
        department (str): Deparment asset is published from.
        bot_url(str): URL of the discord bot that notifies the server.

        Output:
        message (dict): A discord dictionary (json type) of the message that will be published.
        """
        # Sets the message header to color green.
        green_color = 5763719

        # Gets the user name from the discord user open.
        self.user = getpass.getuser()

        # The message template that will be published in discord.
        message = {
            "username": "Pipeline Bot",
            "embeds": [
                {
                    "title": "Asset Published Successfully.",
                    "description": f"""{asset_name} version: {version} for {department} 
                                    has been successfully exported by {self.user}.""",
                    "color": green_color,
                }
            ],
        }

        # Runts the message publishment.
        try:
            response = requests.post(bot_url, json=message)
            response.raise_for_status()
            print("Discord notification sent.")

        # Prints if any error is found.
        except requests.exceptions.RequestException as e:
            print(f"Discord notification failed: {e}")

        return message

    def csv_publisher(self, asset_data):
        current_path = pathlib.Path(self.obj_path)
        db_path = str(current_path.with_suffix("")) + "_metadata.json"
        # print(db_path)
        with open(db_path, "w") as f:
            json.dump(asset_data, f, indent=4)
        # print(f"Registered at {db_path}")
        return asset_data


class ModelPublisher(MyPublisher):
    def verify_assets(self):
        """
        Description:
        Verifies the assets for the modeling publisher.

        Input:
        selection (obj): A selection in maya that you want to export.

        Output:
        None.
        """
        print("-Starting Modeling Validation-")
        # Stores the name prefix sent.
        self.prefix = "geo"
        super().verify_assets(self.prefix)
        # Verifies if the model has engons.
        self.check_topology()

        # Verifies freeze transforms and delet history.
        self.check_transforms()

        # Verifies spawn
        self.check_history()

        # Verifies UVs.
        self.check_uvs()

        print("--Verifying done---")

    def extract_assets(self, output):
        """
        Description:
        Extracts the model and exports it as either obj or fbx.

        Input:
        Output (str): Is the format you want the export to be.

        Output:
        self.obj_path (str): Destination path of the model.
        """
        print("-Starting Export-")
        # Exports the model as fbx or type of model to the destination.
        # Ensures selection
        cmds.select(self.sel)

        # Grabs the location of the scene.
        scene_path = cmds.file(q=True, sn=True)

        # Grabs the name and the root path.
        scenes_folder = pathlib.Path(scene_path)
        # print(f"Pure_path is {scenes_folder}")
        scene_dir = scenes_folder.parents[1]
        # print(f"scene dir: {scene_dir}")
        self.scene_name = os.path.basename(scene_path).split(".")[0]
        # Get the file version.
        self.version = self.scene_name.split("_")[-1]
        # print(f"Scene root name {os.path.basename(scene_dir)}")

        # Makes a new directory.
        asset_folder = f"assets/{self.scene_name}/modeling/"
        asset_dir = os.path.join(scene_dir, asset_folder)
        os.makedirs(asset_dir, exist_ok=True)
        # print(f"Assset dir is {asset_dir}")

        # Create path for the exports.
        self.obj_path = os.path.join(asset_dir, self.scene_name)
        # print(f"Export path {obj_path}")

        # thumbnail_name = f"{scene_name}.jpg"
        # thumbnail_path = os.path.join(asset_dir, thumbnail_name)

        # Exports the object.
        cmds.file(self.obj_path, type=output, pr=True, es=True)

        print("--Export done--")

    def implement_assets(self, description=""):
        """
        Description: Implements the extracted asssets into a database and notifies.

        Input:

        Output:
        """
        # Gets the enviroment path of discord.
        bot = os.environ.get("PIPELINE_DISCORD_BOT")
        # print(bot)
        # Defines the department.
        department = "modeling"

        # Publishes the notification and the csv.
        self.discord_notification(self.scene_name, self.version, department, bot)

        # Gets the current date
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_hash = uuid.uuid4().hex[:8].upper()

        # Establishes the dictionary.
        asset_data = {
            "id": unique_hash,
            "date": timestamp,
            "name": self.scene_name,
            "version": self.version,
            "path": self.obj_path,
            "user": self.user,
            "description": description,
        }
        print("csv printing")
        self.csv_publisher(asset_data)
        print("done csv")

    def check_topology(self):
        """
        Description:
        Checks the selection model for any ngons or double faces.

        Input:
        none

        Output:
        none
        """
        # Reselects and verifies for ngons
        cmds.select(self.sel)

        # Filters the selection to meshes.
        meshes = cmds.ls(self.sel, dag=True, type="mesh", long=True)

        # Selects the meshes.
        cmds.select(meshes)

        # Checks for ngons in the faces.
        cmds.polySelectConstraint(mode=3, type=8, size=3)

        # Adds engons to the list
        ngons = cmds.ls(sl=True)

        # Comes out of the face selection.
        cmds.polySelectConstraint(disable=True)
        if ngons:
            raise PublishError(f"Ngons at: {ngons}")

        # Creates an empty list to store lamina objects.
        lamina_objs = []

        # Check for lamina faces and appends it if so.
        for obj in meshes:
            lamina = cmds.polyInfo(obj, laminaFaces=True)
            if lamina:
                lamina_objs.append(obj)

        # Publishes if an error.
        if lamina_objs:
            raise PublishError(f"Overlapping faces at: {lamina_objs}")

    def check_transforms(self):
        """
        Description:
        Checks the transforms freeze of the selected object.

        Input: None

        Output: None
        """
        # Makes an empty list to append.
        bad_transforms = []
        # It checks each selection.
        for obj in self.sel:
            # Check Translation
            t = cmds.getAttr(f"{obj}.translate")[0]
            # We verify the translation is frozen.
            if abs(t[0]) > 0.001 or abs(t[1]) > 0.001 or abs(t[2]) > 0.001:
                bad_transforms.append(f"{obj} (Translate)")
                continue

            # Check Rotation
            r = cmds.getAttr(f"{obj}.rotate")[0]
            if abs(r[0]) > 0.001 or abs(r[1]) > 0.001 or abs(r[2]) > 0.001:
                bad_transforms.append(f"{obj} (Rotate)")
                continue

            # Check Scale
            s = cmds.getAttr(f"{obj}.scale")[0]
            if (
                abs(s[0] - 1.0) > 0.001
                or abs(s[1] - 1.0) > 0.001
                or abs(s[2] - 1.0) > 0.001
            ):
                bad_transforms.append(f"{obj} (Scale)")
                continue

        # Raise error ONCE at the end
        if bad_transforms:
            raise PublishError(f"Transforms not frozen on: {bad_transforms}")

    def check_history(self):
        """
        Docstring for check_history

        :param self: Description
        """
        bad_obj = []
        for obj in self.sel:
            history = cmds.listHistory(obj, pruneDagObjects=True)
            if history is not None:
                bad_obj.append(obj)
        if bad_obj:
            raise PublishError(f"These objects still contain history: {bad_obj}")

    def check_uvs(self):
        """
        Description: Checksthe uvs of the selected objects

        Input:
        None

        Output:
        None
        """
        for obj in self.sel:
            # Check if the object simply has UVs
            uv_counts = cmds.polyEvaluate(obj, uv=True)

            if uv_counts == 0:
                raise PublishError(f"Object {obj} has no UVs!")


class PublishError(Exception):
    """
    Description: Custom exception for publishing.

    Input: None. Inherist the Exception Class

    Output: None.
    """

    pass
