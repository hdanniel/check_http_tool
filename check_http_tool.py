# coding: utf-8

# optparse: python < 2.7
from optparse import OptionParser
import urllib2
import urlparse
import unittest
import BaseHTTPServer
import time
#from HTMLParser import HTMLParser
from sgmllib import SGMLParser
import StringIO
import gzip

color_green=";32m"
color_green_normal=";92m"
color_red=";31m"
color_blue=";34m"
color_yellow=";33m"
color_default="m"


class JsCssParser(SGMLParser):
      def reset(self):
          SGMLParser.reset(self)
          self.jscss=[]
      def start_link(self,attrs):
          style=False
          for k,v in attrs:
               if (k=='rel') and (v=='stylesheet'):
                  style=True
               if (k=='type') and (v=='text/css'):
                  style=True
          if style:
             href = [v for k, v in attrs if k == 'href']
             if href:
                self.jscss.extend(href)
      def start_script(self,attrs):
          script=False
          for k,v in attrs:
               if (k=='type') and (v=='text/javascript'):
                  script=True
          if script:
             src = [v for k, v in attrs if k == 'src']
             if src:
                self.jscss.extend(src)


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

def gunzip_read(data_gz):
    stream_gz = StringIO.StringIO(data_gz)
    gz = gzip.GzipFile(fileobj=stream_gz)
    return gz.read()
    

class UrlTest():
	def __init__(self):
        	self.time=0
		self.redirect=[]
		self.content_encoding=False
		self.content_type=""
		self.url = ""
	        self.code=0
		self.accept_encoding=  ('Accept-encoding', 'gzip,deflate')
	        self.user_agent= ('User-Agent', 'Mozilla/5.0 (X11; U; Linux x86_64; es-AR; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3')
		self.error= False
		self.content = []
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
		       self.content_type=response.info().get('Content-Type')
		       self.code = response.code
		       self.content = response.read()
		       if self.content_encoding:
		          self.content=gunzip_read(self.content)

                except urllib2.HTTPError,e:
                   response = False
        	   self.error = e.code
        	   self.code = e.code
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
	  redirect = url_test.redirect
	  response_time = url_test.time
	  print 'URL: %s' % (url)
          if url_test.code:
             message_short, message_long = BaseHTTPServer.BaseHTTPRequestHandler.responses[url_test.code]
             print 'Respuesta: %s - %s' % (str(url_test.code), message_short)
	  if redirect:
	     message_redirect = url 
             for redirect_code,redirect_url in redirect[::-1]:
		 message_redirect_code = " ("+str(redirect_code)+") "
	         message_redirect += message_redirect_code
	         message_redirect += " -> " 
	         message_redirect += redirect_url
	     message_redirect_code = " ("+str(url_test.code)+") "
	     message_redirect += message_redirect_code
	     print message_redirect
          if (url_test.code in [200,301,302]):
             print 'Tiempo de Respuesta: %.2f ms' % (response_time*1000)
             if compression :
                print chr(27)+"[0"+color_green+url+" usa compresión http"+chr(27)+"[0m" 
                #print '%s soporta compresión HTTP' % url
             else:
                print chr(27)+"[0"+color_red+url+" usa compresión http"+chr(27)+"[0m" 
                #print '%s no soporta compresión HTTP' % url
             #result.content = result.content.replace("<a&hellip;","")
	     if url_test.content_type.startswith('text/html'):
	        parser = JsCssParser()
                parser.feed(url_test.content)
                parser.close()
                jscss_list=parser.jscss
	        if len(jscss_list)>0:
                   print "Test de Compresión de Componentes"
                for jscss in jscss_list:
                    url_jscss=""
                    if jscss.startswith('http://'):
                       url_jscss=jscss
                    else:
                       url_jscss=urlparse.urljoin(url,jscss)
		    url_component = UrlTest()
		    url_component.url = url_jscss
		    url_component.test()
		    if url_component.content_encoding:
                       message_compression = "OK"
		       color=color_green
                    else:
                       message_compression = "NO"
		       color=color_red
                    print chr(27)+"[0"+color+url_jscss+"\t"+message_compression+chr(27)+"[0m" 

   else:
      p.print_help()

if __name__ == "__main__":
   main()
