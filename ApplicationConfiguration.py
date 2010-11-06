# -*- coding: utf-8 -*-

import ConfigParser
import types
import ApplicationConfigurationParser

AppConfig_ = None

def AppConfig():
    global AppConfig_
    return AppConfig_
    

class ApplicationConfiguration:

    def __init__(self, argv, appgroup):
        global AppConfig_

        if AppConfig_ is not None:
            self = AppConfig_
            return

        self.m_argv = argv
        self.m_appgroup = appgroup
        self.m_config_parser = ApplicationConfigurationParser.ApplicationConfigurationParser()
        
        results = self.m_config_parser.ParseConfig(self.m_argv, self.m_appgroup)

        self.m_app_name = results['APP_NAME']
        self.m_app_root = results['APP_ROOT']
        self.m_app_domain = results['APP_DOMAIN']
        self.m_app_override = results['APP_OVERRIDE']
        self.m_app_user = results['APP_USER']
        self.m_app_config = results['NORMALIZED_APP_CONFIG']
        

        AppConfig_ = self

    def FindValue(self, key, default=None):
        if key in self.m_app_config:
            return self.m_app_config[key]
        
        return default

    def AppName(self):
        return self.m_app_name

    def AppRoot(self):
        return self.m_app_root

    def AppDomain(self):
        return self.m_app_domain

    def AppOverride(self):
        return self.m_app_override

    def AppUser(self):
        return self.m_app_user
        
    def AppConfig(self):
        return self.m_app_config
