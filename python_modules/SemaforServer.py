#!/usr/bin/env python
import sys
import os
import subprocess
import re
import time
#import serial
from thread import *
import zmq
import json
import RPi.GPIO as GPIO
import httplib, urllib
import picamera

class SemaforServer():
    """ Semafor Server """
    
    def __init__(self):
        self.port = "5891"
        self.red = 23
        self.yellow = 17
        self.green = 24
        
        self.callTime = 5
        
        self.emergency = 0
        self.isEmergency = 0
        
        self.lastColorChange = int(time.time())
        
        #self.serverURL = 'http://192.168.2.195:3000/api/devices/updatestatus'
        self.serverURL = '192.168.2.195'
        self.serverCall = '/api/devices/updatestatus'
        self.serverPort = 3000
        
        self.urlPath = "http://192.168.3.216/images/"
        
        self.threadOn = 0
    
    def setup(self):
        #
        print 'setup'
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.red, GPIO.OUT)
        GPIO.setup(self.yellow, GPIO.OUT)
        GPIO.setup(self.green, GPIO.OUT)
        
        GPIO.output(self.green, GPIO.LOW)
        GPIO.output(self.red, GPIO.LOW)
        GPIO.output(self.yellow, GPIO.LOW)
        
        self.redStatus = 0
        self.yellowStatus = 0
        self.greenStatus = 0
        
        self.lastCall = int(time.time())
        
        self.camera = picamera.PiCamera()
        
        self.createServer()
    
    def loop(self):
        #
        print 'loop'
        while True:
            
            if self.threadOn == 0:
                start_new_thread(self.bindZmq, (self.threadOn,))
            
            if self.emergency == 0 and self.isEmergency == 0:
                now = int(time.time())
                if (now - self.lastCall) >= self.callTime:
                    self.lastCall = now
                    self.callServer()
            else:
                self.lastCall = int(time.time())
            
            time.sleep(0.2)
    
    def createServer(self):
        # ZeroMQ Context
        context = zmq.Context()
        # Define the socket using the "Context"
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:%s" % self.port)
        
    def changeLights(self, color):
        if color == 'red':
            if self.redStatus == 0:
                GPIO.output(self.green, GPIO.LOW)
                self.greenStatus = 0
                GPIO.output(self.yellow, GPIO.HIGH)
                self.yellowStatus = 1
                time.sleep(2)
                GPIO.output(self.yellow, GPIO.LOW)
                self.yellowStatus = 0
                GPIO.output(self.red, GPIO.HIGH)
                self.redStatus = 1
            else:
                GPIO.output(self.green, GPIO.LOW)
                self.greenStatus = 0
            
        if color == 'green':
            if self.greenStatus == 0:
                GPIO.output(self.red, GPIO.LOW)
                self.redStatus = 0
                GPIO.output(self.yellow, GPIO.HIGH)
                self.yellowStatus = 1
                time.sleep(2)
                GPIO.output(self.yellow, GPIO.LOW)
                self.yellowStatus = 0
                GPIO.output(self.green, GPIO.HIGH)
                self.greenStatus = 1
            else:
                GPIO.output(self.red, GPIO.LOW)
                self.redStatus = 0
        
        self.lastColorChange = int(time.time())
                
    def status(self):
        message = {}
        message['a'] = {}
        message['a']['red'] = self.redStatus
        message['a']['yellow'] = self.yellowStatus
        message['a']['green'] = self.greenStatus
        
        jsonMessage = json.dumps(message)
        
        try:
            self.socket.send(jsonMessage)
        except Exception:
            print 'status send error'
        
        self.emergency = 0;
    
    def processMessage(self, jsonMessage):
        message = json.loads(jsonMessage)
        print message
        if message['device'] == 'a':
            if message['type'] == 'status':
                self.status()
            if message['type'] == 'color':
                self.changeLights(message['color'])
                self.status()
        elif message['device'] == 'b':
            pass
    
    def clear(self):
        GPIO.cleanup();
        self.socket.close()
    
    def callServer(self):
        message = {}
        message['a'] = {}
        message['a']['state'] = 'emergency' if self.isEmergency == 1 else 'default'
        message['a']['color'] = self.getActualColor()
        message['a']['light'] = 254
        message['a']['lastColorChange'] = self.lastColorChange;
        message['a']['img'] = self.getCamImage()
        message['b'] = {}
        
        print 'Send message to server'
        print json.dumps(message)
        
        try:
            #response = requests.post(self.serverURL, data=json.dumps(message))
            params = json.dumps(message)
            headers = {"Content-type": "application/json","Accept": "text/plain"}
            conn = httplib.HTTPConnection(self.serverURL, self.serverPort)
            try:
                conn.request("POST", self.serverCall, params, headers)
            except Exception:
                conn.close()
                print 'Socket error'
                return
            response = conn.getresponse()
            serverMessage = response.read()
            #print 'Response from server:'
            #print serverMessage
            conn.close()
            self.processServerMessage(serverMessage)
        except httplib.HTTPException as e:
            print e
            print 'Server is not responding'
            print 'try again next time'
    
    def getActualColor(self):
        if self.greenStatus == 1:
            return 'green'
        if self.yellowStatus == 1:
            return 'yellow'
        if self.redStatus == 1:
            return 'red'
    
    def bindZmq(self, test=False):
        self.threadOn = 1
        try:
            message = self.socket.recv()
            print 'Message received'
            print message
            self.emergency = 1
            #start_new_thread(self.processMessage, (message,))
            self.processMessage(message)
            time.sleep(0.2)
            self.threadOn = 0
        except Exception:
            self.threadOn = 0
            #print 'problema'
            #pass
    
    def processServerMessage(self, jsonMessage):
        try:
            message = json.loads(jsonMessage)
            print message
        except Exception:
            print 'Response from server is not JSON'
            return
            
        if 'a' in message:
            amessage = message['a']
            self.changeLights(amessage['color'])
            self.isEmergency = 0 if amessage['state'] == 'default' else 1
            
    def getCamImage(self):
        imgsDir = os.path.abspath(os.path.dirname(__file__) + '/' + '../public/images')
        imagePath = imgsDir + '/'
        imageFile = 'image_' + str(int(time.time())) + '.jpg'
        self.camera.capture(imagePath + imageFile)
        return self.urlPath + imageFile
    
    