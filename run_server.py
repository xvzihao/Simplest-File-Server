import datetime
import socket
import json
import threading
import os
from urllib import parse
"""s = socket.socket()
s.bind(("localhost", 80))
s.listen(3)
conn, addr = s.accept()
r = conn.recv(1024)"""
'''
     Basic Steps of Downloading a file:
          send -> ok
          send -> file(size)
          send -> end

          send -> file_content
'''

#auto create file
l=os.listdir("./")
if 'root' not in l:
    os.mkdir('root')
if 'properties.json' not in l:
    with open('./properties.json','w') as f:
        f.write("""{
    "title": "File Server",
    "server_name": "Simple File Server",
    "owner": "Administrator",
    "port": "80"
}""")
settings = json.load(open("properties.json", 'r'))

def log(content):
    with open('log.log', 'a') as f:
        f.write("["+str(datetime.datetime.now())+"] "+content+'\n')
    print("["+str(datetime.datetime.now())+"] "+content)


class gotf:
    def __init__(self, content):
        self.content = content.decode()
        line = self.content.split('\n')
        self.type, self.target, _ = line[0].split()
        self.target = parse.unquote(self.target)


class http:
    ok = b'HTTP/1.0 200 OK\r\n'

    def file(size):
        return f'Content-Length: {size}\r\nContent-Type: application/octet-stream\r\n'.encode('utf8')
    html = b'Content-Type: text/html; charset=UTF-8\r\n'
    css = b'Content-Type: text/css; charset=UTF-8\r\n'
    end = b'\r\n'


def html_path(path):
    path = parse.unquote(path)
    if '/root' == path[:5]:
        path = path[5:]
    if path[-1] != '/':
        path += '/'
    tmp = '<a href="/root/{target}">{name}/</a> '
    ret = ''
    stack = ''
    for name in path.split('/'):
        if name != '':
            ret += tmp.replace('{name}',
                               name).replace('{target}', stack + name + '/')
            stack += name + '/'
    return ret


def strsize(size):
    k = 1024
    m = k * k
    g = m * k
    if size > g*0.8:
        return str(round(size/g*10)/10)+"GB"
    elif size > m*0.8:
        return str(round(size/m*10)/10)+"MB"
    elif size > k*0.8:
        return str(round(size/k*10)/10)+"KB"
    else:
        return str(size)+"B"


def colume(name, size, link):
    link_type = "Download" if link[-1] != '/' else "Go to"

    if link_type == "Download":
        return f"""            <tr>
                <td class="name">{name}</td>
                <td class="size">{size}</td>
                <td class="link"><a href="{link}" download="{link.split('/')[-1]}">{link_type}</a></td>
            </tr>"""
    return f"""            <tr>
                <td class="name">{name}</td>
                <td class="size">{size}</td>
                <td class="link"><a href="{link}">{link_type}</a></td>
            </tr>"""


with open("./index.html", 'r') as f:
    stdpg = f.read().replace('{title}', settings["title"]).replace(
        '{server_name}', settings["server_name"]).replace('{owner}', settings["owner"])


def request(conn, addr):
    header = conn.recv(1024)
    conn.send(http.ok)
    asr = gotf(header)
    log(str(addr)+' : '+asr.target)
    if asr.target == '/':
        conn.send(http.html)
        conn.send(http.end)
        conn.send(bytes(
            """<script> window.location.href='/root/'; </script>""", encoding='utf8'))
        conn.close()
    else:
        if os.path.isfile('.'+asr.target):
            if 'root' not in asr.target:
                with open('.'+asr.target, 'rb') as f:
                    r = None
                    conn.send(http.css)
                    conn.send(http.end)
                    while r != b'':
                        r = f.read(1024**2*64)
                        conn.send(r)
                conn.close()
            else:
                with open('.'+asr.target, 'rb') as f:
                    r = None
                    conn.send(http.file(os.path.getsize('.'+asr.target)))
                    conn.send(http.end)
                    while r != b'':
                        r = f.read(1024**2*64)
                        conn.send(r)
                conn.close()
        else:
            conn.send(http.html)
            conn.send(http.end)
            html = stdpg.replace("{path}", html_path(asr.target))
            added = ''
            for item in os.listdir('.'+asr.target):
                added += colume(item, strsize(os.path.getsize('.'+asr.target+item)), asr.target +
                                (item if os.path.isfile('.'+asr.target+item) else item+'/'))
            html = html.replace("{add}", added)

            conn.send(bytes(html, encoding='utf8'))
            conn.close()


def main():
    s = socket.socket()
    ip = socket.gethostbyname_ex(socket.gethostname())[-1][-1]
    port = int(settings['port'])
    s.bind((ip, port))
    log("Server Starts on " + str((ip, port)))
    s.listen(1024)

    while True:
        conn, addr = s.accept()
        threading.Thread(target=request, args=(conn, addr)).start()


if __name__ == '__main__':
    main()
