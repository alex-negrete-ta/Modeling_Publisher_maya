from PySide6 import QtWidgets, QtCore
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from publishing import ModelPublisher, PublishError


def main():
    # 1. Find the Maya Main Window (The 'Shortest' Pure-Qt way)
    maya_win = next(
        (
            w
            for w in QtWidgets.QApplication.topLevelWidgets()
            if w.objectName() == "MayaWindow"
        ),
        None,
    )

    # 2. Cleanup existing UI by object name (not title)
    win_id = "ModelPublisherUniqueName"
    for widget in QtWidgets.QApplication.topLevelWidgets():
        if widget.objectName() == win_id:
            widget.close()
            widget.deleteLater()

    # 3. Parent the UI to Maya to keep it alive
    pub_win = PublisherWindow(parent=maya_win)
    pub_win.setObjectName(win_id)
    pub_win.setWindowFlags(QtCore.Qt.Window)
    pub_win.show()


class PublishStepWidget(QtWidgets.QWidget):
    """A reusable widget for a single CVEI step."""

    def __init__(self, label_text, parent=None):
        super(PublishStepWidget, self).__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        self.indicator = QtWidgets.QLabel()
        self.indicator.setFixedSize(15, 15)
        self.set_status("idle")

        self.label = QtWidgets.QLabel(label_text)
        self.label.setStyleSheet("font-weight: bold; font-size: 11px;")

        layout.addWidget(self.indicator)
        layout.addWidget(self.label)
        layout.addStretch()

    def set_status(self, status):
        """Updates color: idle (grey), running (yellow), success (green), fail (red)"""
        colors = {
            "idle": "#555555",
            "running": "#FFD700",
            "success": "#4CAF50",
            "fail": "#F44336",
        }
        color = colors.get(status, "#555555")
        self.indicator.setStyleSheet(
            f"background-color: {color}; border-radius: 7px; border: 1px solid #222;"
        )


class PublisherWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(PublisherWindow, self).__init__(parent)
        self.setWindowTitle("Pipeline Publisher - Model")
        self.setMinimumSize(400, 550)
        self.setWindowFlags(QtCore.Qt.Window)

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        # Format Selection
        self.format_label = QtWidgets.QLabel("Export Format:")
        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(["OBJexport", "FBX export"])

        # CVEI Status Steps
        self.step_c = PublishStepWidget("COLLECT")
        self.step_v = PublishStepWidget("VERIFY")
        self.step_e = PublishStepWidget("EXTRACT")
        self.step_i = PublishStepWidget("IMPLEMENT")

        self.steps = [self.step_c, self.step_v, self.step_e, self.step_i]

        # Log Window
        self.log_output = QtWidgets.QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Logs will appear here...")
        self.log_output.setStyleSheet(
            "background-color: #1a1a1a; color: #dcdcdc; font-family: 'Consolas';"
        )

        # Publish Button
        self.publish_btn = QtWidgets.QPushButton("PUBLISH ASSET")
        self.publish_btn.setFixedHeight(40)
        self.publish_btn.setStyleSheet("background-color: #3d7199; font-weight: bold;")
        self.publish_btn.clicked.connect(self.run_publish)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Options Group
        opt_group = QtWidgets.QGroupBox("Configuration")
        opt_layout = QtWidgets.QFormLayout(opt_group)
        opt_layout.addRow(self.format_label, self.format_combo)
        main_layout.addWidget(opt_group)

        # Status Group
        status_group = QtWidgets.QGroupBox("Process Status")
        status_layout = QtWidgets.QVBoxLayout(status_group)
        for step in self.steps:
            status_layout.addWidget(step)
        main_layout.addWidget(status_group)

        # Logs
        main_layout.addWidget(QtWidgets.QLabel("Output Logs:"))
        main_layout.addWidget(self.log_output)

        main_layout.addWidget(self.publish_btn)

    def write_log(self, text, is_error=False):
        color = "red" if is_error else "#88ff88"
        self.log_output.appendHtml(f'<span style="color:{color};">{text}</span>')
        QtCore.QCoreApplication.processEvents()  # Force UI update

    def reset_ui(self):
        for step in self.steps:
            step.set_status("idle")
        self.log_output.clear()

    def run_publish(self):
        self.reset_ui()
        selection = cmds.ls(sl=True)

        # Initialize Publisher
        # Note: Replace 'your_shotgrid_api_link' with your actual endpoint
        pub = ModelPublisher(selection, "http://shotgrid.api.link")
        output_format = self.format_combo.currentText()

        try:
            # 1. COLLECT
            self.step_c.set_status("running")
            pub.collect_assets()
            self.step_c.set_status("success")
            self.write_log("Step: Collect successful.")

            # 2. VERIFY
            self.step_v.set_status("running")
            pub.verify_assets()  # This calls the ModelPublisher override
            self.step_v.set_status("success")
            self.write_log("Step: Verification (Topology, Transforms, History) passed.")

            # 3. EXTRACT
            self.step_e.set_status("running")
            pub.extract_assets(output=output_format)
            self.step_e.set_status("success")
            path = pub.obj_path
            print(path)
            self.write_log(f"Step: Exported to {path} as {output_format}.")

            # 4. IMPLEMENT
            self.step_i.set_status("running")
            pub.implement_assets()
            self.step_i.set_status("success")
            self.write_log("Step: Discord notification sent.")

            QtWidgets.QMessageBox.information(
                self, "Success", "Asset Published Successfully!"
            )

        except PublishError as e:
            # Determine where it failed based on status
            for step in self.steps:
                if (
                    step.indicator.styleSheet().find("#FFD700") != -1
                ):  # if it was running
                    step.set_status("fail")

            self.write_log(f"PUBLISH ERROR: {str(e)}", is_error=True)
            cmds.warning(f"Publish failed: {e}")

        except Exception as e:
            self.write_log(f"CRITICAL SYSTEM ERROR: {str(e)}", is_error=True)
            import traceback

            self.write_log(traceback.format_exc(), is_error=True)


if __name__ == "__main__":
    main()
