#!/usr/bin/python
# coding: utf8
"""
Copyright (c) 2015-2016 __Loxoll__. All rights reserved.
"""
# 123 !/usr/bin/env python
import os, sys, shutil
import zipfile
import compileall
import datetime

file_name = os.path.basename(__file__)

class ZipUtil(object):
    def __init__(self):
        pass

    def ZipTrace(self):
        # create zip file
        zippath = './zip/'
        if not os.path.exists(zippath): os.makedirs(zippath)

        zip_file_name = zippath + datetime.datetime.now().strftime('LX%Y%m%d%H%M%S.zip')
        zip_trace = zipfile.ZipFile(zip_file_name, 'w')
        print "zip_file_name = ", zip_file_name

        # put Trace into zip file
        for root, dirs, files in os.walk('./trace'):
            for file in files:
                target_file = os.path.join(root, file)
                zip_trace.write(target_file)
        # put Source into zip file
        for root, dirs, files in os.walk('./source'):
            for file in files:
                target_file = os.path.join(root, file)
                zip_trace.write(target_file)
        # put Data into zip file
        for root, dirs, files in os.walk('./data'):
            for file in files:
                target_file = os.path.join(root, file)
                zip_trace.write(target_file)
        
        zip_trace.write('./Config.ini')
        zip_trace.write('./GUImain.py')
        zip_trace.close()
        return zip_file_name


    def UnzipFile(self, zip_file_name, out_path):
        if os.path.exists(out_path):
            shutil.rmtree(out_path)
        
        os.makedirs(out_path)

        zip_ref = zipfile.ZipFile(zip_file_name, 'r')
        zip_ref.extractall(out_path)
        zip_ref.close()


    def ZipRelease(self, path, zip):
        for root, dirs, files in os.walk(path):
            for file in files:
                if root == './':
                    if file[-3:] == '.py':
                        target_file = os.path.join(root, file)
                        compileall.compile_file(target_file, force=True)
                        zip.write(target_file+'c')

                    if file == 'Config.ini' or file == 'README':
                        zip.write(os.path.join(root, file))
                
#                    if file == 'engine_40.txt':         # test file
#                        print "---", os.path.join(root, file)
#                        zip.write(os.path.join(root, file))
                
    def ZipSource(self, path, zip):
        for root, dirs, files in os.walk(path):
            for file in files:
                if root == './':
                    if file[-3:] == '.py':
                        print "---", os.path.join(root, file)
                        zip.write(os.path.join(root, file))

                    if file == 'Main' or file == 'ZipUtil' or file == 'Config.ini' :
                        print "---", os.path.join(root, file)
                        zip.write(os.path.join(root, file))
                
                    if file == 'engine_40.txt':         # test file
                        print "---", os.path.join(root, file)
                        zip.write(os.path.join(root, file))
                        
    
if __name__ == '__main__':
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-10]
    time_now = time_now.replace(' ', '-')
    time_now = time_now.replace(':', '-')
#
# Get the Company Name for the release name.zip
# 
    myfile = open('DisplayDashboard.py', 'r')
    lines = myfile.readlines()
    myfile.close()    
    for idx in range(len(lines)):
        if lines[idx].startswith('COMPANY'): break
    if idx == len(lines):
        company = 'Loxoll'
    else:
        info = lines[idx].split()
        company = info[2][1:-1]
#    
    zip_r = zipfile.ZipFile("%sGUI-%s.zip" % (company, time_now), 'w')
    zip_a = zipfile.ZipFile("%sARC-%s.zip" % (company, time_now), 'w')
    z = ZipUtil()
    z.ZipRelease('./', zip_r)
    z.ZipSource('./', zip_a)
    zip_r.close()    
    zip_a.close()
    
    if not os.path.exists('./zipfile'): os.makedirs('./zipfile')
    os.system("mv *.zip ./zipfile")
    