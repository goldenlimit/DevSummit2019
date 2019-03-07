## using python to talk with current feature serivce, then uisng admin api get specific url to add view
import urllib.request
import urllib.parse
import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

createServiceUrl = 'https://test.mapsqa.arcgis.com/sharing/rest/content/users/TestAdministrator/createService'
serviceUrl ='https://servicesqa.arcgis.com/T33eop2F1qYOrIKA/arcgis/rest/services/DevSummitDemo/FeatureServer/'
adminRestUrl = 'https://servicesqa.arcgis.com/T33eop2F1qYOrIKA/arcgis/rest/admin/services/DevSummitDemo/FeatureServer/'
serviceLayersUrl = 'https://servicesqa.arcgis.com/T33eop2F1qYOrIKA/arcgis/rest/services/DevSummitDemo/FeatureServer/layers'
accessToken = 'HUdZ6q24d1IEVEzAYeqnfiVbdyDH51ErEOTy8VIIY5qNasPc4C4T8Ei4a61q8MXOpIWxMrumEtCA4tspAkO0rjGS5pWLK3ojUTdHXSNoR0i2alm74E6suYjAeDcD7ZWJh5NNc1vM1sbTVBE2dqULZ1FPmYdTVGHrjRy3SGVeJAhMNmh7BZ-o1w8y333ozKSQ90Ry24WnfVPf6ybm7fXIP5-7TWdGTUMq5Ss8FmqzsrU.'
createParams = '{"name":"DevSummitDemo_PythonCreatedView","isView":true,"sourceSchemaChangesAllowed":true,"isUpdatableView":true,"spatialReference":{"wkid":102100,"latestWkid":3857},"initialExtent":{"xmin":-5009536.543108713,"ymin":9586388.516507195,"xmax":-5009217.628285908,"ymax":9586707.817600405,"spatialReference":{"wkid":102100,"latestWkid":3857}},"capabilities":"Query","preserveLayerIds":false}'
sourceServiceName = 'DevSummitDemo'
deleteItemUrl = 'https://servicesqa.arcgis.com/sharing/content/users/TestAdministrator/items/itemID/delete'
viewServiceUrl = 'https://servicesqa.arcgis.com/T33eop2F1qYOrIKA/arcgis/rest/services/DevSummitDemo_PythonCreatedView/FeatureServer'

createServiceHeaders = {}
createServiceHeaders['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
createServiceHeaders["Host"] = 'test.mapsqa.arcgis.com'
createServiceHeaders['Origin'] = 'https://test.mapsqa.arcgis.com'
createServiceHeaders['Connection'] = 'keep-alive'

serviceLayerHeaders = {}
serviceLayerHeaders['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
serviceLayerHeaders["Host"] = 'servicesqa.arcgis.com'
serviceLayerHeaders['Origin'] = 'https://servicesqa.arcgis.com'
serviceLayerHeaders['Connection'] = 'keep-alive'

originLayerInfoPayload = urllib.parse.urlencode({'f': 'json', 'token': accessToken}).encode('ascii')
getLayerInfoRequest = urllib.request.Request(serviceLayersUrl, data=originLayerInfoPayload, headers=serviceLayerHeaders)
getLayerInfoResponse = urllib.request.urlopen(getLayerInfoRequest)
parentLayerInfoString = getLayerInfoResponse.read().decode('utf-8')
print(parentLayerInfoString)

#Create View Service Request
createViewServicePayload = urllib.parse.urlencode({'f': 'json', 'createParameters': createParams,
                                                   'outputType': 'featureService', 'isView': 'true',
                                                   'token': accessToken}).encode('ascii')
createViewServiceRequest = urllib.request.Request(createServiceUrl,
                                                  data=createViewServicePayload,
                                                  headers=createServiceHeaders)
createViewServiceResponse = urllib.request.urlopen(createViewServiceRequest)

##dynamically parse out the url for view service url
viewServiceInfoString = createViewServiceResponse.read().decode('utf-8')
viewServiceJSON = json.loads(viewServiceInfoString)
#viewServiceUrl = viewServiceJSON["encodedServiceURL"]

def str_append(s, n):
    output = s + n
    return output

viewServiceAdminUrl = viewServiceUrl.replace('rest/', 'rest/admin/')
viewServiceAdminAddDefUrl = str_append(viewServiceAdminUrl, '/addToDefinition')

#Get parent(original) service layers info
#REMEMBER to parse urlencode for request body
originLayerInfoPayload = urllib.parse.urlencode({'f': 'json', 'token': accessToken}).encode('ascii')
getLayerInfoRequest = urllib.request.Request(serviceLayersUrl, data=originLayerInfoPayload, headers=serviceLayerHeaders)
getLayerInfoResponse = urllib.request.urlopen(getLayerInfoRequest)

##Parse HTTPResponse to string
parentLayerInfoString = getLayerInfoResponse.read().decode('utf-8')
dictJSONDecode = json.loads(parentLayerInfoString)

dictLayers = dictJSONDecode['layers']
dictTables = dictJSONDecode['tables']

layerNumber = 0

newViewDict = {'layers': dictLayers, 'tables': dictTables}
for layer in dictLayers:
    if not layer:
        break
    else:
        adminLayerInfoPerLayer = {
            "viewLayerDefinition": {"sourceServiceName": 'DevSummitDemo', "sourceLayerId": layerNumber,
                                    "sourceLayerFields": '*'}}

        print(adminLayerInfoPerLayer)
        adminLayerInfoPerLayerDict = {'adminLayerInfo': adminLayerInfoPerLayer}
        newViewDict['layers'][layerNumber] = layer
        newViewDict['layers'][layerNumber].update(adminLayerInfoPerLayerDict)
        newViewDict['layers'][layerNumber].pop('fields', None)
        newViewDict['layers'][layerNumber].pop('indexes', None)
        newViewDict['layers'][layerNumber].pop('relationships', None)

    layerNumber += 1

for table in dictTables:
    if not table:
        break
    else:
        adminLayerInfoPerTable = (
                "{'viewLayerDefinition':{'sourceServiceName':'%s','sourceLayerId':%s,'sourceLayerFields':'*'}}" % (
        'DevSummitDemo', layerNumber))

        newViewDict['tables'][layerNumber] = table
        newViewDict['tables'][layerNumber].update('adminLayerInfo', adminLayerInfoPerTable)
        newViewDict['tables'][layerNumber].pop('fields', None)
        newViewDict['tables'][layerNumber].pop('indexes', None)
        newViewDict['tables'][layerNumber].pop('relationships', None)

    layerNumber += 1

newViewJSON = json.dumps(newViewDict)
print(newViewJSON)

addToDefinitionViewPayload = urllib.parse.urlencode({'f': 'json', 'addToDefinition': newViewJSON, 'token': accessToken}).encode('ascii')
# parse to dynamically fetch view service url

data = {"f": "json", "addToDefinition": newViewJSON, "token": accessToken}
r = requests.post(viewServiceAdminAddDefUrl, data=data, verify=False)
print('Add View Result: ----------------\n')
print(r.content)

# addToDefinitionViewRequest = urllib.request.Request(viewServiceAdminAddDefUrl, data=addToDefinitionViewPayload)
# addToDefinitionViewResponse = urllib.request.urlopen(addToDefinitionViewRequest)
# print(addToDefinitionViewResponse)