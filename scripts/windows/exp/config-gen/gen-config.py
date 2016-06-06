import os
import sys
import copy
from reg_apps import *
import reg_config

global article #array
global tags_repo #array
global parameters #array
global apps #array
global actived_apps #array
global root_dir #str

class Sentence:
    def __init__(self, content = '', include = [], exclude = []):
        self.content = content 
        self.include = copy.copy(include)
        self.exclude = copy.copy(exclude)

class App:
    def __init__(self, path, tags):
        global tags_repo
        global parameters
        self.path = path
        for tag in tags:
            if tag not in tags_repo : 
                raise Exception("tag " + tag + " is not registered")
        self.tags = copy.copy(tags)
        self.tags = self.tags + parameters

    def satisfied(self, include = [], exclude = []):
        for i in include:
            if i not in self.tags:
                return False
        for e in exclude:
            if e in self.tags:
                return False;
        return True

    def __str__(self):
        ret = "path : " + self.path + os.linesep
        ret = ret + "tags: "
        for tag in self.tags:
            ret = ret + tag + " "
        return ret

def init_global_vars():
    global article
    global apps
    global parameters
    global tags_repo
    global output_file_name
    global actived_apps
    global root_dir
    article = []
    apps = []
    parameters = []
    tags_repo = []
    output_file_name = 'config.ini'
    actived_apps = []
    root_dir = '.'
    
def register_parameters():
    global parameters
    global tags_repo
    global output_file_name
    global root_dir
    print sys.argv
    args = copy.copy(sys.argv)
    for i in range (1, len(args)):
        key = args[i].split('=')[0]
        value = args[i].split('=')[1]
        if key == 'name':
            output_file_name = value
        elif key == 'batch_size':
            reg_config.set_max_batch_size(value)
        elif key == 'root':
            root_dir = value
        elif key == 'tags':
            tags = value.split(',')
            for tag in tags:
                if tag not in tags_repo:
                    raise Exception("tag " + tag + " is not registered")
                parameters.append(tag)
        elif key == 'apps':
            tags = value.split(',')
            for tag in tags:
                if tag not in tags_repo:
                    raise Exception("tag " + tag + " is not registered")
                actived_apps.append(tag)
        else:
            raise Exception("unsupported parameters : " + key)
    print tags_repo
    print parameters

def add_sentence(content, include = [], exclude = []):
    global article
    global tags_repo
    if (content is None):
        raise Exception("content is null");
    for inc in include :
        if inc not in tags_repo:
            raise Exception("tag " + inc + " is not registered")
    for exc in exclude :
        if exc not in tags_repo:
            raise Exception("tag " + exc + " is not registered")
    s = Sentence(content, include, exclude)
    article.append(s)

def register_apps():
    global apps
    global output_file_name
    global actived_apps
    global root_dir
    
    confs = app_configs()
    dirs = []
    for conf in confs:
        path = root_dir + '/' + conf[0]
        tags = conf[1]
        actived = True
        if len(actived_apps) > 0:
            actived = False
            for tag in tags:
                if tag in actived_apps:
                    actived = True
        if actived == True:
            dirs.append(path)
            apps.append(App(path+ '/' + output_file_name, tags))
    for app in apps:
        print app

    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)

def register_tags():
    global tags_repo
    tags_repo = tags_repo + used_tags()

def gen_article():
    confs = reg_config.get_config_sentence()
    for s in confs:
        add_sentence(s[0], s[1], s[2])

def gen_config_file():
    global article
    global apps
    
    for app in apps:
        f = open(app.path, 'w')
        for s in article:
            if app.satisfied(s.include, s.exclude):
                f.write(s.content + '\n') 
        f.close()


if __name__ == '__main__':
    init_global_vars()
    register_tags()
    register_parameters() 
    register_apps()
    gen_article()
    gen_config_file()

    print "\nsuccess!"
