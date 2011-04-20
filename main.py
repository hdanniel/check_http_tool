# coding: utf-8

# optparse: python < 2.7
from optparse import OptionParser
import urllib2
import urlparse

def get_valid_url(url):
    url_parser=urlparse.urlparse(url)
    if (url_parser.scheme in ['http','https']):
       return url
    else:
       return 'http://'+url

def gzip_test(url):
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip,deflate') 
    request.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux x86_64; es-AR; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3') 
    response = urllib2.urlopen(request)
    if (response.info().get('Content-Encoding')):
       return True
    else:
       return False

if __name__ == "__main__":
   p = OptionParser(description="HTTP Compression Test", prog="front.py", version="0.1", usage="%prog [url]")
   #p.add_option('--url', '-u', default="http://www.google.com")
   options, arguments = p.parse_args()
   if len(arguments) > 0:
      for url in arguments:
	  url = get_valid_url(url)
          if gzip_test(url) :
             print '%s soporta compresión HTTP' % url
          else:
             print '%s no soporta compresión HTTP' % url
              
   else:
      p.print_help()
