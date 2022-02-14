from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.utils.fitimage import FitImage

from detect import DetectFruitHealth
from kivy.properties import BooleanProperty, ObjectProperty
from kivymd.toast import toast
from kivy.clock import Clock
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog

PRIMARY_EXTERNAL_STORAGE = '/'
if platform == "android":
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

    from android.storage import primary_external_storage_path

    PRIMARY_EXTERNAL_STORAGE = primary_external_storage_path()


class CustomLayout(BoxLayout):
    detect = BooleanProperty(defaultvalue=False)  # Image loaded and program is ready to infer
    detecting = BooleanProperty(defaultvalue=False)  # Program is in inference process
    dialog = ObjectProperty(defaultvalue=None)

    def __init__(self, **kwargs):
        super(CustomLayout, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.current_image = 'placeholder.png'
        self.image_model_content = None
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )
        self.detection_model = DetectFruitHealth()

    def file_manager_open(self):
        self.file_manager.show(PRIMARY_EXTERNAL_STORAGE)  # output manager to the screen
        self.manager_open = True

    def select_path(self, path):
        """It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file;
        """

        self.exit_manager()
        self.detect = True
        self.ids.inference_img.source = path
        self.current_image = path
        if PRIMARY_EXTERNAL_STORAGE != '/':
            path = path.replace(PRIMARY_EXTERNAL_STORAGE, '')
        self.ids.img_info.text = path

    def exit_manager(self, *args):
        """Called when the user reaches the root of the directory tree."""

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Called when buttons are pressed on the mobile device."""

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def infer(self, img_path):
        if img_path == 'placeholder.png':
            toast("Please first select an image!")
            return
        self.detecting = True
        self.detection_model.run(img_path=img_path)
        self.detect = False
        Clock.schedule_interval(callback=self.check_inference_result, timeout=.2)

    def check_inference_result(self, dt):
        if self.detection_model.output_image_path is not None:
            self.ids.inference_img.source = self.detection_model.output_image_path
            self.current_image = self.detection_model.output_image_path
            self.detecting = False
            self.detection_model.output_image_path = None
            return False

    def open_dialog(self):
        if not self.dialog:
            self.image_model_content = FitImage(source=self.current_image, size_hint_y=None, height="248dp")
            self.dialog = MDDialog(
                title="Image Modal View",
                type="custom",
                content_cls=self.image_model_content,
            )
        else:
            self.image_model_content.source = self.current_image
        self.dialog.open()


class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        kv = Builder.load_file('main.kv')
        return kv


if __name__ == '__main__':
    MainApp().run()
