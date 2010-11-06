#!/usr/bin/python

import sys
import os
import glob
import pwd
import types

from ApplicationConfigurationGrammar import ApplicationConfigurationGrammar
from ApplicationConfigurationGrammar import GrammarTypes

application_configuration_root = "config"

class ApplicationConfigurationParser:

    def __init__(self):
        self.m_file_app_config = {}
        self.m_cl_app_config = {}
        self.m_normalized_app_config = {}
        self.m_file_grammar = ApplicationConfigurationGrammar(GrammarTypes.FileGrammar)
        self.m_cl_grammar = ApplicationConfigurationGrammar(GrammarTypes.CommandLineGrammar)

    
    def NormalizeAppName(self, path):
        idx = path.rfind('/')
        
        if (idx == -1):
            return path

        return path[(idx + 1):]


    def NormalizeConfig(self):
        for key, value in self.m_file_app_config.iteritems():
            keyParts = key.split(".", 1)
            domain = keyParts[0]
            keyProper = keyParts[1]

            if (domain == self.m_app_domain):
                self.m_normalized_app_config[keyProper] = value
            elif(( domain == "*") and ( (self.m_app_domain + "." + keyProper) not in self.m_file_app_config ) ):
                self.m_normalized_app_config[keyProper] = value
                
                
        self.m_normalized_app_config.update(self.m_cl_app_config)

    def CheckConfigDir(self):
        if (self.m_app_root is None):
            return False
        
        exists = os.path.isdir(self.m_app_root + "/" + application_configuration_root)
        
        if (not exists):
            return False

        self.m_global_exists = os.path.isdir(self.m_app_root + "/" + application_configuration_root + "/global")
        self.m_appgroup_exists = os.path.isdir(self.m_app_root + "/" + application_configuration_root + "/appgroup")
        self.m_app_exists = os.path.isdir(self.m_app_root + "/" + application_configuration_root + "/app")
        self.m_app_user_exists = os.path.isdir(self.m_app_root + "/" + application_configuration_root + "/user")
        self.m_app_host_exists = os.path.isdir(self.m_app_root + "/" + application_configuration_root + "/host")
        self.m_app_override_exists = (self.m_app_override != '' and os.path.isdir(self.m_app_root + "/" + application_configuration_root + "/override"))
        
        return True

    def LoadGlobal(self):
        if (not self.m_global_exists):
            return False
        
        files = glob.glob(self.m_app_root + "/" + application_configuration_root + "/global/*.cfg")

        for file in files:
            self.m_file_grammar.parseFile(file, self.m_file_app_config)

    def LoadAppgroup(self):
        if (not self.m_appgroup_exists):
            return False
        
        filename = self.m_app_root + "/" + application_configuration_root + "/appgroup/" + self.m_appgroup + ".cfg"
        
        if (os.path.exists(filename)):
            self.m_file_grammar.parseFile(filename, self.m_file_app_config)
            return True
        else:
            return False

    def LoadApp(self):
        if (not self.m_app_exists):
            return False

        filename = self.m_app_root + "/" + application_configuration_root + "/app/" + self.m_app_name + ".cfg"
        
        if (os.path.exists(filename)):
            self.m_file_grammar.parseFile(filename, self.m_file_app_config)
            return True
        else:
            return False

    def LoadUser(self):
        if (not self.m_app_user_exists):
            return False

        filename = self.m_app_root + "/" + application_configuration_root + "/user/" + self.m_app_user + ".cfg"
        
        if (os.path.exists(filename)):
            self.m_file_grammar.parseFile(filename, self.m_file_app_config)
            return True
        else:
            return False

    def LoadHost(self):
        if (not self.m_app_host_exists):
            return False

        filename = self.m_app_root + "/" + application_configuration_root + "/host/" + self.m_app_host + ".cfg"
        
        if (os.path.exists(filename)):
            self.m_file_grammar.parseFile(filename, self.m_file_app_config)
            return True
        else:
            return False

    def LoadOverride(self):
        if (self.m_app_override == ''):
            return True

        if (not self.m_app_override_exists):
            print 'override dir doesnt exist'
            return False
        
        filename = self.m_app_root + "/" + application_configuration_root + "/override/" + self.m_app_override
        
        if (os.path.exists(filename)):
            self.m_file_grammar.parseFile(filename, self.m_file_app_config)
            return True
        else:
            return False
        
    def ParseConfig(self, argv, appgroup):
        self.m_argv = argv
        self.m_appgroup = appgroup
        self.m_app_name = self.NormalizeAppName(argv[0])
        self.m_cl_app_config = self.m_cl_grammar.parseString(' '.join(argv[1:]))
        self.m_app_user = pwd.getpwuid(os.getuid())[0]
        self.m_app_host = 'sv-test-01'

        if ( ('root' not in self.m_cl_app_config) or (not isinstance(self.m_cl_app_config['root'], types.StringType) ) ):
            raise ('--root not found!')
        
        if ( ('domain' not in self.m_cl_app_config) or (not isinstance(self.m_cl_app_config['domain'], types.StringType) ) ):
            raise ('--domain not found!')
        
        self.m_app_root = self.m_cl_app_config['root']
        del self.m_cl_app_config['root']
        
        self.m_app_domain = self.m_cl_app_config['domain']
        del self.m_cl_app_config['domain']

        self.m_app_override = ''
        if ('override' in self.m_cl_app_config):
            self.m_app_override = self.m_cl_app_config['override']
            del self.m_cl_app_config['override']
            
        if (not self.CheckConfigDir()):
            raise('Could not find "swing-config" directory under specified root')

        self.LoadGlobal()
        self.LoadAppgroup()
        self.LoadApp()
        self.LoadHost()
        self.LoadUser()
        self.LoadOverride()
        self.NormalizeConfig()

        return {'APP_NAME':self.m_app_name,
                'APP_ROOT':self.m_app_root,
                'APP_DOMAIN':self.m_app_domain,
                'APP_OVERRIDE':self.m_app_override,
                'CL_APP_CONFIG':self.m_cl_app_config,
                'FILE_APP_CONFIG':self.m_file_app_config,
                'NORMALIZED_APP_CONFIG':self.m_normalized_app_config,
                'APP_GROUP':self.m_appgroup,
                'APP_USER':self.m_app_user}
    

