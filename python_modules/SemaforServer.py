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

class SemaforServer():
    """ Semafor Server """
    
    def __init__(self):
        self.port = "5891"
        self.red = 23
        self.yellow = 17
        self.green = 18
    
    def setup(self):
        #
        print 'setup'
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.red, GPIO.OUT)
        GPIO.setup(self.yellow, GPIO.OUT)
        GPIO.setup(self.green, GPIO.OUT)
        
        self.redStatus = 0
        self.yellowStatus = 0
        self.greenStatus = 0
        
        self.createServer()
    
    def loop(self):
        #
        print 'loop'
        while True:
            try:
                message = self.socket.recv()
                print 'Message received'
                print message
                start_new_thread(self.processMessage, (message,))
            except Exception:
                print 'problema'
            
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
                
    def status(self):
        message = {}
        message['red'] = self.redStatus
        message['yellow'] = self.yellowStatus
        message['green'] = self.greenStatus
        jsonMessage = json.dumps(message)
        try:
            self.socket.send(jsonMessage)
        except Exception:
            print 'status send error'
    
    def processMessage(self, jsonMessage):
        message = json.loads(jsonMessage)
        if message['type'] == 'status':
            self.status()
        if message['type'] == 'color':
            self.changeLights(message['color'])
            self.status()
    
    