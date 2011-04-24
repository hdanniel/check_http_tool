# coding: utf-8

# optparse: python < 2.7
from optparse import OptionParser
import urllib2
import urlparse
import unittest
import BaseHTTPServer
import time

#class test_get_valid_url(unittest.TestCase):
#      def test(self): 
          #self.assert_(get_valid_url('www.google.com')) 
          #self.assert_(get_valid_url('http://www.google.com')) 
#          self.assert_(get_valid_url('test')) 
#          self.assert_(get_valid_url(1)) 


class RedirectHandler(urllib2.HTTPRedirectHandler):
	def __init__(self):
        	self.redirect_list = [] 

        def http_error_301(self, req, fp, code, msg, headers):  
                result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
                result.redirect = code
		#self.redirect_list.append((code,result.geturl()))
		self.redirect_list.append((code,headers['Location']))
		return result 

        def http_error_302(self, req, fp, code, msg, headers):
                result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)              
                result.redirect = code                                
		#self.redirect_list.append((code,result.geturl()))
		self.redirect_list.append((code,headers['Location']))
		return result 

class UrlTest():
	def __init__(self):
        	self.time=0
		self.redirect=[]
		self.content_encoding=False
		self.url = ""
	        self.code=0
		self.accept_encoding=  ('Accept-encoding', 'gzip,deflate')
	        self.user_agent= ('User-Agent', 'Mozilla/5.0 (X11; U; Linux x86_64; es-AR; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3')
		self.error= False
	def test(self):
                request = urllib2.Request(self.url)
		header_key,header_val= self.accept_encoding
                request.add_header(header_key, header_val)
		header_key,header_val= self.user_agent
                request.add_header(header_key, header_val)
    		rh = RedirectHandler()
    		redirect = []
    		time_download=0
    		opener = urllib2.build_opener(rh)
    		urllib2.install_opener(opener)
    		try:
        	    time_start=time.time()
                    response = urllib2.urlopen(request)
                    time_end=time.time()
                    self.time = time_end - time_start
        	    if response:
           	       self.error = False
                       self.redirect = rh.redirect_list
		       self.content_encoding=response.info().get('Content-Encoding')
		       self.code = response.code
                except urllib2.HTTPError,e:
                   response = False
        	   self.error = e.code
                except urllib2.URLError,e:
                   response = False
                   self.error = False

def get_valid_url(url):
    try:
        url_parser=urlparse.urlparse(url)
        if (url_parser.scheme in ['http','https']):
           return url
        else:
           return 'http://'+url
    except AttributeError:
           return False 

def main():
   p = OptionParser(description="HTTP Compression Test", prog="front.py", version="0.1", usage="%prog [url]")
   options, arguments = p.parse_args()
   if len(arguments) > 0:
      for url in arguments:
          url = get_valid_url(url)
	  url_test = UrlTest()
	  url_test.url = url
	  url_test.test()
	  compression = url_test.content_encoding
	  code = url_test.code
	  redirect = url_test.redirect
	  response_time = url_test.time
          message_short, message_long = BaseHTTPServer.BaseHTTPRequestHandler.responses[code]
	  print 'URL: %s' % (url)
          print 'Respuesta: %s - %s' % (str(code), message_short)
	  if redirect:
	     message_redirect = url 
             for redirect_code,redirect_url in redirect[::-1]:
		 message_redirect_code = " ("+str(redirect_code)+") "
	         message_redirect += message_redirect_code
	         message_redirect += " -> " 
	         message_redirect += redirect_url
	     message_redirect_code = " ("+str(code)+") "
	     message_redirect += message_redirect_code
	     print message_redirect
          if (code in [200,301,302]):
             print 'Tiempo de Respuesta: %.2f ms' % (response_time*1000)
             if compression :
                print '%s soporta compresión HTTP' % url
             else:
                print '%s no soporta compresión HTTP' % url

   else:
      p.print_help()

if __name__ == "__main__":
   main()
