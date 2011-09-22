import os
import pystache

class Base(pystache.View):
    template_path = os.path.dirname(__file__) + '/templates'

class Index(Base):
    def title(self):
        return 'Dashboard - Cider'
    
    def terminalLink(self):
        host = self.get('host', None)
        host = host[:host.find(':')]
        return 'https://' + host + ':4200'

class Editor(Base):
    def title(self):
        return self.file() + ' - Cider'
    
    def file(self):
        return self.get('file', None)

    def text(self):
        try:
            f = open(os.path.join(os.path.dirname(__file__), self.file()), 'r')
            return f.read().replace('{{', '~' + 'dlb').replace('}}', '~' + 'drb')
        except Exception:
            return ''

    def mode(self):
        file = self.file()
        ext = file[(file.rfind('.') + 1):]

        if ext == 'c' or ext == 'cpp':
            return 'c_cpp'
        elif ext == 'cs':
            return 'csharp'
        elif ext == 'css':
            return 'css'
        elif ext == 'html' or ext == 'mustache':
            return 'html'
        elif ext == 'java':
            return 'java'
        elif ext == 'js':
            return 'javascript'
        elif ext == 'json':
            return 'json'
        elif ext == 'php':
            return 'php'
        elif ext == 'py':
            return 'python'
        elif ext == 'rb':
            return 'ruby'
        elif ext == 'svg':
            return 'svg'
        elif ext == 'xml':
            return 'xml'
        else:
            return ''

class FileManager(Base):
    def title(self):
        return self.path() + ' - Cider'
        
    def base(self):
        return os.path.dirname(__file__)
    
    def fileList(self):
        base = self.base()
        path = self.path()
        
        files = []
        files = os.listdir(os.path.join(base, path))
        
        for i in range(len(files)):
            files[i] = {
                'name' : files[i],
                'isFile' : os.path.isfile(
                    os.path.join(base, path, files[i])
                ),
                'path' : path
            }
        
        return files
    
    def path(self):
        path = self.get('path', None)
        if path != None or path != '':
            return path
        else:
            return ''
    
    def up(self):
        path = self.path()
        
        if path != '' and path.rfind('/') > -1:
            return path[:path.rfind('/')]
        else:
            return ''
