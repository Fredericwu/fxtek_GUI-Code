"""
Control JSON Module

Created by Susan Cheng on 2015-11-27.
Copyright (c) 2015-2016 __Loxoll__. All rights reserved.
"""
#
# This module is designed to manage all JSON related activities.
#
import sys, os
import json

file_name = os.path.basename(__file__)

#
# SDU executive class, service all SDU related requests 
#
class xJSON(object):

    def __init__(self):
#        dbg.printDBG1(file_name, "initiate xJSON")
        self.data = {}
#   
#   
    def ConvertToJSON(self, input):
        # pretty printing of json-formatted string
        print json.dumps(eval(input), sort_keys=True, indent=4)
#
    def getData(self, json_input):
        try:
            self.data = json.loads(json_input)

            # pretty printing of json-formatted string
            print json.dumps(self.data, sort_keys=True, indent=4)

            print "JSON parsing example: ", self.data['one']
            print "Complex JSON parsing example: ", self.data['two']['list'][1]['item']

        except (ValueError, KeyError, TypeError):
            print "JSON format error"

    def putData(self, result):
        self.data['result'] = result
        print ""
        print json.dumps(self.data, indent=4)
        

if __name__ == '__main__':
    p = xJSON()
    p.getData('{ "one": 1, "two": { "list": [ {"item":"A"},{"item":"B"} ] }, "result": "" }')
    p.putData('Normal')
    sys.exit()

