import os
import requests
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import json

opsman_host = 'https://opsman.'+os.environ['PCF_ERT_DOMAIN']
opsman_user = os.environ['OPS_MGR_USR']
opsman_pwd = os.environ['OPS_MGR_PWD']
client_id='opsman'
client_secret=''
username=opsman_user
password=opsman_pwd
refresh_url=opsman_host+'/uaa/oauth/token'


def associate_vm_ext(client, cf_guid, job, vm_ext):
    print 'associate: '+str(job)+' || '+str(vm_ext)
    vmext = {"name": job['name']+'_ext', "cloud_properties": vm_ext}
    resp = client.put(opsman_host+'/api/v0/staged/vm_extensions/'+job['name']+'_ext', verify=False, json=vmext)
    if resp.status_code != 200:
        print 'got non-200 status code adding the vm extension (%d).  Exiting' % resp.status_code
        exit(1)
    job_resource_config = client.get(opsman_host+'/api/v0/staged/products/'+cf_guid+'/jobs/'+job['guid']+'/resource_config', verify=False).json()
    job_resource_config['additional_vm_extensions'].append(job['name']+'_ext')
    update_job_config_resp = client.put(opsman_host + '/api/v0/staged/products/' + cf_guid + '/jobs/' + job['guid'] + '/resource_config',
               verify=False, json=job_resource_config)

    # job_resource_config = client.get(
    #     opsman_host + '/api/v0/staged/products/' + cf_guid + '/jobs/' + job['guid'] + '/resource_config',
    #     verify=False).json()
    # print job_resource_config

    if update_job_config_resp.status_code != 200:
        print 'got non-200 status code associating the vm extension (%d).  Exiting' % update_job_config_resp.status_code
        exit(1)

    # job_resource_config['additional_vm_extensions'].pop()

    # update_job_config_resp = client.put(
    #     opsman_host + '/api/v0/staged/products/' + cf_guid + '/jobs/' + job['guid'] + '/resource_config',
    #     verify=False, json=job_resource_config)

    # resp2 = client.delete(opsman_host+'/api/v0/staged/vm_extensions/'+job['name']+'_ext', verify=False)
    print resp

def update_vm_exts():
    oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
    token = oauth.fetch_token(token_url=opsman_host+'/uaa/oauth/token',
                                   username=username, password=password, client_id=client_id,
                                   client_secret=client_secret, verify=False)

    print token

    client = OAuth2Session(client_id, token=token)
    prod_resp = client.get(opsman_host+'/api/v0/staged/products', verify=False)
    prods = prod_resp.json()

    print prods

    for prod in prods:
        if prod['type'] == 'cf':
            cf_guid = prod['guid']
            break

    jobs_resp = client.get(opsman_host+'/api/v0/staged/products/'+cf_guid+'/jobs')
    jobs = jobs_resp.json()['jobs']
    print jobs

    with open('vm_extensions.json') as f:
        vm_exts = json.load(f)
        for job in jobs:
            if job['name'] in vm_exts:
                associate_vm_ext(client, cf_guid, job, vm_exts[job['name']])

    vme_resp = client.get(opsman_host + '/api/v0/staged/vm_extensions', verify=False)
    print vme_resp.text

if __name__ == "__main__":
    update_vm_exts()
