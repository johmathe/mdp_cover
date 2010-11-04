#!/usr/bin/python
# Author: Johan Mathe (johmathe@nonutc.fr)
# License: LGPL

import base64
import datetime
import hashlib
import hmac
import sys
import time
import urllib
import xml.dom.minidom

AWS_KEY = ''
SECRET_KEY = ''
AWS_HOST = 'ecs.amazonaws.com'
AWS_URI = '/onca/xml'

class NoCoverAvailable(Exception):
  pass

def QueryAmazonApi(artist, album):
  amazonid = AWS_KEY
  req = {}
  dstamp = datetime.datetime.utcfromtimestamp(time.time())
  req['Timestamp'] = dstamp.strftime('%Y-%m-%dT%H:%M:%S.000Z')
  req['Service'] = 'AWSECommerceService'
  req['Operation'] = 'ItemSearch'
  req['Artist'] = artist
  req['Keywords'] = album
  req['MerchantId'] = 'All'
  req['Version'] = '2009-03-31'
  req['SearchIndex'] = 'Music'
  req['ResponseGroup'] = 'Images'
  req['AWSAccessKeyId'] = amazonid
  xml_result = AmazonQuery(req)
  return xml_result

def ExtractBestCoverUrl(xmlstring):
  doc = xml.dom.minidom.parseString(xmlstring)
  images = doc.getElementsByTagName("LargeImage")
  urls = {}
  for i in images:
    height = int(i.getElementsByTagName('Height')[0].firstChild.nodeValue)
    width = int(i.getElementsByTagName('Width')[0].firstChild.nodeValue)
    size = height * width
    if size not in urls:
      url = i.getElementsByTagName('URL')
      urls[size] = url[0].firstChild.nodeValue
  sizes = urls.keys()
  sizes.sort()
  try:
    url = urls[sizes[-1]]
  except IndexError:
    raise NoCoverAvailable()
  return url

def CreateAmazonSignature(to_sign):
  h = hmac.new(SECRET_KEY, to_sign, hashlib.sha256)
  sig = base64.b64encode(h.digest())
  return urllib.quote(sig)

def AmazonQuery(query):
  URI_String = []
  for keyword, value in sorted(query.items()):
    URI_String.append('%s=%s' % (keyword, urllib.quote(value)))
  req =  '&'.join(URI_String)
  to_sign = 'GET\n%s\n%s\n%s' % (AWS_HOST, AWS_URI, req)
  signature = CreateAmazonSignature(to_sign)
  req += '&Signature=%s' % signature

  baseurl = 'http://ecs.amazonaws.com/onca/xml?'
  apicall = baseurl + req
  res = urllib.urlopen(apicall).read()
  return res

def GetUrl(artist, album):
  xml_result = QueryAmazonApi(artist, album)
  return ExtractBestCoverUrl(xml_result)

if __name__ == '__main__':
  # that could be seen as an integration test :)
  print GetUrl('Piazzolla', 'Genius')
