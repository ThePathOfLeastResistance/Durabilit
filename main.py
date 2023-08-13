from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
import easyocr
import pandas as pd
import os
from dotenv import load_dotenv, dotenv_values
import openai
load_dotenv()
openai.api_key = os.getenv("api")




x = 0

class CamApp(MDApp):
    def build(self):
        self.layout = MDBoxLayout(orientation="vertical")

        self.image = Image()
        self.layout.add_widget(self.image)
        self.save_img_button = MDRaisedButton(
            text="Take Picture",
            pos_hint={"center_x": .5, "center_y": .5},
            size_hint=(None, None))
        self.layout.add_widget(self.save_img_button)
        # This could be 1 or zero depends
        self.capture = cv2.VideoCapture(0)
        self.save_img_button.bind(on_press=self.take_pic)
        Clock.schedule_interval(self.load_video, 1.0 / 30.0)
        return self.layout

    def load_video(self, *args):
        ret, frame = self.capture.read()
        self.image_frame = frame
        #buf1 = cv2.flip(frame, 0)
        #buf = buf1.tostring()
        buf = cv2.flip(frame, 0).tostring()
        image_texture = Texture.create(
           size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
        self.image.texture = image_texture


    def take_pic(self, *args):
        global x
        x += 0
        image_name = f"{x}.png"
        cv2.imwrite(image_name, self.image_frame)
        amswer = self.read_pic(name=image_name)

        print(amswer['choices'][0]['message']['content'])




    def read_pic(self, name):
        reader = easyocr.Reader(['en'], gpu = False)
        results = reader.readtext(name)
        ingredent = pd.DataFrame(results, columns = ['bbox', 'text','conf'])
        return self.test(ingredent['text'].tolist())

    def test(self, listin):
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = [{"role":"system", "content":f"I am making a product, I am using a list of ingredient, however, the ingreident list got mixed up and contains spelling errors and other unimportant words, fliter thorugh the list to find words that can be ingredents), this is my list of ingreidents: [{list}], based on the ingreidents, give it a score out of 100 based on the ingreients's impact on the potential enviroment and things like that, JUST say the score, then seperated by a period, give a 50 word explaination on how the ingrdents affect the envoirment, if in any way you cannot anwer the question respond with JUST 'ERROR, retake Picture''."}]
        )
        return response

if __name__ == "__main__":
    CamApp().run()
