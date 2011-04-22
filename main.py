# coding: utf-8

# optparse: python < 2.7
from optparse import OptionParser
import urllib2
import urlparse
import unittest
import BaseHTTPServer

#class test_get_valid_url(unittest.TestCase):
#      def test(self): 
          #self.assert_(get_valid_url('www.google.com')) 
          #self.assert_(get_valid_url('http://www.google.com')) 
#          self.assert_(get_valid_url('test')) 
#          self.assert_(get_valid_url(1)) 

class RedirectHandler(urllib2.HTTPRedirectHandler):
        def http_error_301(self, req, fp, code, msg, headers):  
                result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)              
                result.redirect = code
		return result 

        def http_error_302(self, req, fp, code, msg, headers):
                result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)              
                result.redirect = code                                
		return result 

def get_valid_url(url):
    try:
        url_parser=urlparse.urlparse(url)
        if (url_parser.scheme in ['http','https']):
           return url
        else:
           return 'http://'+url
    except AttributeError:
           return False 

def get_response(url):
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip,deflate') 
    request.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux x86_64; es-AR; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3')
    opener = urllib2.build_opener(RedirectHandler)
    urllib2.install_opener(opener) 
    try:
        response = urllib2.urlopen(request)
        if response: 
           error = False
    except urllib2.HTTPError,e:
        response = False
        error = e.code
    except urllib2.URLError,e:
        response = False
        error = False
    return response, error
      
def test_url(url):
    response,error = get_response(url)
    redirect = False
    if hasattr(response, 'redirect'):
       redirect = response.redirect 
    if (response):
       return response.info().get('Content-Encoding'), response.code, response.geturl(),redirect
    else:
       return False,error,url,False

def main():
   p = OptionParser(description="HTTP Compression Test", prog="front.py", version="0.1", usage="%prog [url]")
   options, arguments = p.parse_args()
   if len(arguments) > 0:
      for url in arguments:
          url = get_valid_url(url)
          compression, code, real_url,redirect = test_url(url)
          url_redirect = "" 
          if redirect: 
	     code = redirect
	     url_redirect = real_url
          message_short, message_long = BaseHTTPServer.BaseHTTPRequestHandler.responses[code]
          print str(code) + " : " + message_short + " " + url_redirect
          if (code in [200,301,302]):
             if compression :
                print '%s soporta compresión HTTP' % url
             else:
                print '%s no soporta compresión HTTP' % url

   else:
      p.print_help()

if __name__ == "__main__":
   main()
