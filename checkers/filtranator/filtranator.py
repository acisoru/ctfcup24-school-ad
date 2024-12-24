import requests
import pytesseract
import io
import sys
from PIL import Image, ImageFont, ImageDraw, ImageColor
from checklib import *
from PIL.PngImagePlugin import PngInfo

PORT = 6969


def text_to_image(
    text: str,
    font_filepath: str,
    font_size: int,
    color: (int, int, int),  # color is in RGB
    font_align="center",
):
    #font = ImageFont.load_default(18)
    font = ImageFont.load_default(18)
    #box = font.getsize_multiline(text)
    img = Image.new("RGBA", (400,400),color='black')
    draw = ImageDraw.Draw(img)
    draw_point = (0, 0)
    draw.multiline_text(draw_point, text, font=font, fill=color, align=font_align)
    return img


class CheckMachine:
    @property
    def url(self):
        return f"http://{self.c.host}:{self.port}"

    def __init__(self, checker: BaseChecker):
        self.c = checker
        self.port = PORT

    def register(self, session: requests.Session, username: str, password: str,status: Status.MUMBLE):
        url = f"{self.url}/register"
        resp = session.post(url, data={"username": username, "password": password})
        self.c.assert_(resp.text, "<p1>Sucessfully registered</p1>")
        resp = session.post(
            url, data={"username": username, "password": password}
        )
        self.c.assert_(resp.text, "<p1>User alredy exist</p1>",status)

    def logout(self, session: requests.Session,status: Status.MUMBLE):
        url = f"{self.url}/logout"
        resp = session.get(url)
        self.c.assert_(resp.text,'<p1>Sucessfully logout</p1>',status)

    def login(
        self, session: requests.Session, username: str, password: str, status: Status
    ):
        url = f"{self.url}/login"
        resp = session.post(url, data={"username": username, "password": password})
        self.c.assert_(resp.text, "<p1>Sucessfully logged in</p1>",status)
        resp = session.post(url, data={"username": username, "password": password})
        self.c.assert_(resp.text, "<p1>Already logged in</p1>",status)

    def put_image(self, session: requests.Session, text: str,status: Status.MUMBLE):
        url = f"{self.url}/apply_filter"
        kek = text_to_image(
            text,
            "./MonaSansCondensed-Black.otf",
            40,
            (120, 120, 120),
        )
        metadata = PngInfo()
        metadata.add_text("flag", text)
        bytex = io.BytesIO()
        kek.save(bytex,format='PNG',pnginfo = metadata)
        imgkek = bytex.getvalue()
        files = {"image": ("img", imgkek, "multipart/form-data", {"Expires": "0"})}
        resp = session.post(
            url,
            data={"filter": "none", "filename": "flag"},
            files=files,
        )
        self.c.assert_(resp.text, "<p1>Image saved</p1>",status)

    def get_image(self, session: requests.Session) -> str:
        url = f"{self.url}/images"
        resp = session.get(url)
        img_bytes = io.BytesIO(resp.content)
        if img_bytes.getbuffer().nbytes == 0:
            return ''
        img = Image.open(img_bytes)
        print(img.text.keys(),file=sys.stderr)
        text = img.text['flag']#pytesseract.image_to_string(img)
        return text
