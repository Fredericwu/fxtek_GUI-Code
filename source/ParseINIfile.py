"""
Copyright (c) 2015-2016 __Loxoll__. All rights reserved.
"""
#
#  cfg = ParseUtil('Config.ini')
#  ip = cfg['Engine1']['IP']
#
import codecs

class ParseINIfile(dict):
    def __init__(self, f):
        self.f = f
        self.__read()

    def CompanyName(self):
        myfile = open('Config.ini', 'r')
        lines = myfile.readlines()
        myfile.close()    
        for idx in range(len(lines)):
            if lines[idx].startswith('COMPANY'): break
            
        if idx == len(lines):
            company = 'Loxoll'
        else:
            info = lines[idx].split()
            company = info[2][1:-1]
        return company
    
 
    def __read(self):

        f = codecs.open(self.f, encoding='utf-8')
        dic = self
        
        for line in f:
            if not line.startswith("#") and line.strip() != "":
                index = line.find('#')
                while (line[index-1] == '\\'):
                    index = line.find('#', index+1)
                line = line[:index]
                line = line.replace('\\#', '#')
                line = line.strip()
                if line.startswith("["):
                    sections = line[1:-1].split('.')
                    dic = self
                    for section in sections:
                        if section not in dic:
                            dic[section] = {}
                        dic = dic[section]
                else:
                    if not self:
                        dic['global'] = {}
                        dic = dic['global'] 
                    parts = line.split("=", 1)
                    dic[parts[0].strip()] = parts[1].strip()
