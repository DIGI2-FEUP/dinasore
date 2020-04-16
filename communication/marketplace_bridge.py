import requests
from pip._internal import main as pipmain
import os
import sys
import logging
from importlib import import_module
import threading
import subprocess
# import flask

class MarketplaceBridge: 

    fbDetailPath = '/function-block'

    protocol = 'http://'
    mpHttpAddress = ''
    mpHttpPort = ''
    mpFtpAddress = ''
    mpFtpPort = ''

    @classmethod
    def initializeGenericRequester(mp,mpHttpAddress,mpHttpPort,mpFtpAddress,mpFtpPort=21,secure=False):

        mp.protocol = 'https://' if secure else 'http://' 
        print(mp.protocol,mp.mpHttpAddress)
        mp.mpHttpAddress = mp.protocol + mpHttpAddress
        mp.mpHttpPort = mpHttpPort
        mp.mpFtpAddress = mpFtpAddress
        mp.mpFtpPort = mpFtpPort

        # print(Flask.__init__)

    @classmethod
    def getFbDetails(mp,fbType):

        path = mp.mpHttpAddress + ':' + str(mp.mpHttpPort) + mp.fbDetailPath + '/' + fbType
        request = requests.get(path)
        response = request.json()
        if response['state']['error'] == True :
            print('Function Block not found on Marketplace')
        else:
            fbInfo = response['result']
            fbCategory = fbInfo['fbCategoryName']
            fbExternalDependencies = fbInfo['fbExternalDependencies']
            print(fbCategory,fbExternalDependencies)
            mp.installDependencies(fbExternalDependencies)
            

    @classmethod
    def installDependencies(mp,dependencies):
        print(dependencies)
        for dependency in dependencies:
            try:
                i = import_module(dependency['edName'])
                print('imported',i)
            except ImportError:
                try:
                    print('installing')
                    # pipmain(['install',dependency['edName'],'--quiet','--user'])
                    subprocess.call(["pip", "install", dependency['edName']])
                except Exception:
                    print(Exception)
                    print('exception')
                    pass
                # print(ValueError)
        print('end')

    @classmethod
    def downloadFunctionBlock(mp, fbType, fbCategory):
        