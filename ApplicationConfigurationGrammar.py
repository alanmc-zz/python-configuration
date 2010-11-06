#!/usr/bin/python

import types
import pyparsing
from Enumerate import Enumerate

GrammarTypes = Enumerate('FileGrammar CommandLineGrammar')

class GenericPair:
    
    def __init__(self, first, second):
        self.first = first
        self.second = second

class ArrayDelimiter:

    def __init__(self):
        pass

class MapDelimiter:

    def __init__(self):
        pass


class ApplicationConfigurationGrammar:
    
    def __init__(self, grammarType):

        if ( grammarType != GrammarTypes.FileGrammar and grammarType != GrammarTypes.CommandLineGrammar):
            raise("Invalid Grammar Type Specified")
    
        self.m_grammar_type = grammarType
        self.m_stack =[]
        self.m_config = {}

        self.m_value = pyparsing.Forward()

        self.m_boolean = ( pyparsing.CaselessLiteral("t") ^ pyparsing.CaselessLiteral("f") ^ pyparsing.CaselessLiteral("true") ^ pyparsing.CaselessLiteral("false") )
        self.m_boolean.setParseAction(self.pushBoolean)

        self.m_number = pyparsing.Word( pyparsing.nums )
        self.m_number.setParseAction(self.pushNumber)

        if (grammarType == GrammarTypes.CommandLineGrammar):
            self.m_string = pyparsing.Word( pyparsing.alphanums + "!@$%^&*_+`~|./")
        else:
            self.m_string = ( pyparsing.Literal("\"").suppress() + pyparsing.Word( pyparsing.alphanums + " !@#$%^&*()-_+=`~[{]}\|;:,<.>/?'") + pyparsing.Literal("\"").suppress() )

        self.m_string.setParseAction(self.pushString)

        self.m_datespec = ( pyparsing.CaselessLiteral("m") | pyparsing.CaselessLiteral("h") | pyparsing.CaselessLiteral("d") | pyparsing.CaselessLiteral("w") | pyparsing.CaselessLiteral("y") )
        self.m_timestamp = pyparsing.Combine( pyparsing.OneOrMore( pyparsing.Word(pyparsing.nums) ) + self.m_datespec )
        self.m_timestamp.setParseAction(self.pushTimestamp)

        self.m_array_begin = pyparsing.Literal("[")
        self.m_array_begin.setParseAction(self.startArray)

        self.m_array_end = pyparsing.Literal("]")
        self.m_array_end.setParseAction(self.endArray)
        
        self.m_array = ( self.m_array_begin + self.m_value + pyparsing.ZeroOrMore (  pyparsing.Literal(",").suppress() + self.m_value ) +  self.m_array_end )

        self.m_pair = ( self.m_string + pyparsing.Literal(":").suppress() + self.m_value )
        self.m_pair.setParseAction( self.createPair )

        self.m_map_begin = pyparsing.Literal("{")
        self.m_map_begin.setParseAction( self.startMap )

        self.m_map_end = pyparsing.Literal("}")
        self.m_map_end.setParseAction( self.endMap )

        self.m_map = self.m_map_begin + self.m_pair + pyparsing.ZeroOrMore( pyparsing.Literal(",").suppress() + self.m_pair ) + self.m_map_end

        if (grammarType == GrammarTypes.CommandLineGrammar):
            self.m_value << ( self.m_timestamp | self.m_number | self.m_array | self.m_map | self.m_string )
        else:
            self.m_value << ( self.m_timestamp | self.m_number | self.m_string | self.m_array | self.m_map | self.m_boolean )


        if (grammarType == GrammarTypes.CommandLineGrammar):
            self.m_key = ( pyparsing.Literal("--").suppress() + pyparsing.Word( pyparsing.alphanums + "_.") )
        else:
            self.m_key = pyparsing.Combine( ( pyparsing.Literal("*") | pyparsing.Word( pyparsing.alphanums ) ) + pyparsing.Literal(".") + pyparsing.Word( pyparsing.alphanums + "_.") )

        self.m_key.setParseAction( self.pushKey )
        
        if (grammarType == GrammarTypes.CommandLineGrammar):
            self.m_entry = self.m_key + pyparsing.Literal("=").suppress() + self.m_value
        else:
            self.m_entry = self.m_key + pyparsing.Literal("=").suppress() + self.m_value + pyparsing.Literal(";").suppress()
        self.m_entry.setParseAction( self.createPair )

        self.m_bool_entry = ( pyparsing.Literal("--").suppress() + pyparsing.Word( pyparsing.alphanums + "_.") )
        self.m_bool_entry.setParseAction( self.createBoolPair )

        if (grammarType == GrammarTypes.CommandLineGrammar):
            self.m_configuration = pyparsing.OneOrMore( self.m_entry | self.m_bool_entry )
        else:
            self.m_configuration = pyparsing.OneOrMore( self.m_entry )

        self.m_configuration.setParseAction( self.endConfiguration )


    def pushKey(self, strg, loc, toks):
        self.m_stack.append(toks[0])

    def pushString(self, strg, loc, toks):
        self.m_stack.append(toks[0])

    def pushNumber(self, strg, loc, toks):
        self.m_stack.append(int(toks[0]))

    def pushBoolean(self, strg, loc, toks):
        bool = toks[0]
        if (bool == "t" or bool == "true"):
            self.m_stack.append(True)
        else:
            self.m_stack.append(False)
        
    def pushTimestamp(self, strg, loc, toks):
        timestampStr = toks[0]
        index = len(timestampStr) - 1
        dateSpec = timestampStr[index]
    
        timestamp = int(timestampStr[0:index])
        
        newTimestamp = timestamp
        
        if (dateSpec == "m"):
            newTimestamp = (timestamp * 60)
        elif (dateSpec == "h"):
            newTimestamp = (timestamp * 60 * 60)
        elif (dateSpec == "d"):
            newTimestamp = (timestamp * 60 * 60 * 24)
        elif (dateSpec == "w"):
            newTimestamp = (timestamp * 60 * 60 * 24 * 7)
        elif (dateSpec == "y"):
            newTimestamp = (timestamp * 60 * 60 * 24 * 365)

        self.m_stack.append(newTimestamp)

    def createPair(self):
        element2 = self.m_stack.pop()
        element1 = self.m_stack.pop()
        pair = GenericPair(element1, element2)

        self.m_stack.append(pair)

    def createBoolPair(self):
        element1 = self.m_stack.pop()
        pair = GenericPair(element1, True)

        self.m_stack.append(pair)

    def startArray(self):
        self.m_stack.append(ArrayDelimiter())

    def endArray(self):
        a = []
    
        while (len(self.m_stack) > 0):
            
            element = self.m_stack.pop()
            
            if ( isinstance(element, ArrayDelimiter) ):
                break
        
            a.append(element)
        
        self.m_stack.append(a)

    def startMap(self):
        self.m_stack.append(MapDelimiter())

    def endMap(self):

        newMap = {}

        while (len(self.m_stack) > 0):
        
            element = self.m_stack.pop()

            if ( isinstance(element, MapDelimiter) ):
                break

            if ( not (isinstance(element, GenericPair)) ):
                continue
        
            newMap[element.first] = element.second
        
        self.m_stack.append(newMap)

    def endConfiguration(self):

        while (len(self.m_stack) > 0):
        
            element = self.m_stack.pop()

            if ( not isinstance(element, GenericPair) ):
                continue

            self.m_config[element.first] = element.second


    def parseFile(self, filePath, output=None):
        if output is None:
            output={}

        self.m_config = output
        self.m_configuration.parseFile(filePath)
        return self.m_config


    def parseString(self, input, output=None):
        if output is None:
            output={}

        self.m_config = output
        self.m_configuration.parseString(input)
        return self.m_config


