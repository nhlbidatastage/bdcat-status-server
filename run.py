# import boto3
import json
import uuid
import requests
import time
import logging
import os
import datetime

from google.cloud import bigquery
from google.oauth2.service_account import Credentials

from google.api_core.exceptions import Conflict
from typing import Union

from gen3.auth import Gen3Auth
# is_healthy() on these endpoints == all the same endpoint
from gen3.jobs import Gen3Jobs
from gen3.index import Gen3Index
from gen3.metadata import Gen3Metadata

import sevenbridges as sbg

import PicSureClient, PicSureHpdsLib

from utils.svg import SERVICE_OK, SERVICE_ERROR, SERVICE_UNKNOWN, make_last_updated_svg

log = logging.getLogger(__name__)
# bucket = 'status-svg-dont-delete-me-ask-lon'
# s3 = boto3.resource('s3', region_name='us-west-2')
credentials = Credentials.from_service_account_file('gcp-creds.json')
client = bigquery.Client(project='unc-renci-bdc-itwg', credentials=credentials)
os.environ['SB_API_ENDPOINT'] = 'https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2'


def getuser():
    return os.environ.get('LOGNAME') or os.environ.get('USER') or os.environ.get('LNAME') or os.environ.get('USERNAME')


def get_latest_pipeline_status():
    PRIVATE_TOKEN = os.environ['GITLAB_READ_TOKEN']
    HOST = 'https://biodata-integration-tests.net'
    BRANCH = 'prod'
    PROJECT_NUM = 3

    job_status_url = f'{HOST}/api/v4/projects/{PROJECT_NUM}/pipelines'
    response = requests.get(job_status_url, headers={'PRIVATE-TOKEN': PRIVATE_TOKEN})
    response.raise_for_status()

    latest = {'id': 0}
    for pipeline in response.json():
        if pipeline['ref'] == BRANCH:
            if pipeline['id'] > latest['id'] and pipeline['status'] not in ['running', 'pending']:
                latest = pipeline
    return latest.get('status', 'pending')


def post_svg(system: str, subsystem: str, ok: Union[bool, str]):
    key = f'{system}.svg' if subsystem == 'overall' else f'{system}/{subsystem.replace(" ", "_").lower()}.svg'
#     if ok == 'Time':
#         s3.Object(bucket, key).put(Body=make_last_updated_svg(), ACL='public-read', ContentType='image/svg+xml')
#     elif ok in ('Not Implemented Yet', 'unknown'):
#         s3.Object(bucket, key).put(Body=SERVICE_UNKNOWN, ACL='public-read', ContentType='image/svg+xml')
    if ok is True:
#         s3.Object(bucket, key).put(Body=SERVICE_OK, ACL='public-read', ContentType='image/svg+xml')
        post_status_to_big_query(system=system, subsystem=subsystem, up=1, create=True)
    elif ok is False:
#         s3.Object(bucket, key).put(Body=SERVICE_ERROR, ACL='public-read', ContentType='image/svg+xml')
        post_status_to_big_query(system=system, subsystem=subsystem, up=0, create=True)
    else:
        raise RuntimeError(f'Unknown value for "ok" status: {ok}')
#     print(f'{"OKAY" if ok else "----"}: {(bucket, key)}')


def post_leonardo_svgs():
    system = 'leonardo'
    response = requests.get('https://notebooks.firecloud.org/status')  # production
    if response.ok:
        response_json = response.json()
    all_healthy = True
    for subsystem in ("Database", "Sam"):
        if response.ok:
            if not response_json['systems'][subsystem]['ok']:
                all_healthy = False
            post_svg(system=system,
                     subsystem=subsystem,
                     ok=response_json['systems'][subsystem]['ok'])
        else:
            post_svg(system=system,
                     subsystem=subsystem,
                     ok=False)

    if response.ok:
        if not response_json['ok']:
            all_healthy = False
        post_svg(system=system,
                 subsystem='overall',
                 ok=all_healthy)
    else:
        post_svg(system=system,
                 subsystem='overall',
                 ok=False)


def post_bond_svgs():
    system = 'bond'
    subsystems = ('fence', 'dcf-fence', 'anvil', 'kids-first', 'cache', 'datastore', 'sam')
    response = requests.get('https://broad-bond-prod.appspot.com/api/status/v1/status')  # production
    if response.ok:
        response_json = response.json()
    all_healthy = True
    for subsystem in (0, 1, 2, 3, 4, 5, 6):
        if response.ok:
            if response_json['subsystems'][subsystem]['subsystem'] not in subsystems:
                print('\nWARNING\n===========\nThe Bond API format has changed!\n===========\nWARNING\n')
            if not response_json['subsystems'][subsystem]['ok']:
                all_healthy = False
            post_svg(system=system,
                     subsystem=response_json['subsystems'][subsystem]['subsystem'],
                     ok=response_json['subsystems'][subsystem]['ok'])
        else:
            try:
                response_json = response.json()
                subsystem_name = response_json['subsystems'][subsystem]['subsystem']
            except:
                subsystem_name = subsystems[subsystem]
            post_svg(system=system,
                     subsystem=subsystem_name,
                     ok=False)

    if response.ok:
        if not response_json['ok']:
            all_healthy = False
        post_svg(system=system,
                 subsystem='overall',
                 ok=all_healthy)
    else:
        post_svg(system=system,
                 subsystem='overall',
                 ok=False)


def post_terra_svgs():
    system = 'terra'
    response = requests.get('https://api.firecloud.org/status')  # production
    if response.ok:
        response_json = response.json()
    all_healthy = True
    for subsystem in ("Thurloe", "Sam", "Consent", "Rawls",
                      "Agora", "GoogleBuckets", "LibraryIndex", "OntologyIndex"):
        if response.ok:
            if not response_json['systems'][subsystem]['ok']:
                all_healthy = False
            post_svg(system=system,
                     subsystem=subsystem,
                     ok=response_json['systems'][subsystem]['ok'])
        else:
            post_svg(system=system,
                     subsystem=subsystem,
                     ok=False)

    if response.ok:
        if not response_json['ok']:
            all_healthy = False
        post_svg(system=system,
                 subsystem='overall',
                 ok=all_healthy)
    else:
        post_svg(system=system,
                 subsystem='overall',
                 ok=False)


def post_dockstore_svgs():
    system = 'dockstore'
    all_healthy = True
    for subsystem in ("discuss.dockstore.org", "dockstore search", "dockstore webservice", "dockstore.org", "docs.dockstore.org"):
        if subsystem in ("discuss.dockstore.org", "dockstore.org", "docs.dockstore.org"):
            endpoint = f'https://{subsystem}'
            response = requests.head(endpoint)
        elif subsystem == 'dockstore webservice':
            endpoint = 'https://dockstore.org/api/swagger.json'
            response = requests.head(endpoint)
        elif subsystem == 'dockstore search':
            endpoint = 'https://dockstore.org/api/metadata/elasticSearch'
            response = requests.get(endpoint)

        if not response.ok:
            all_healthy = False
        post_svg(system=system,
                 subsystem=subsystem,
                 ok=response.ok)

    post_svg(system=system,
             subsystem='overall',
             ok=all_healthy)


def post_biocat_documentation_svgs():
    system = 'biocat_documentation'
    subsystem = 'bdcatalyst.gitbook.io'

    # cloudflare will return a 503 if you poll too often (<=60 seconds)
    response = requests.head('https://bdcatalyst.gitbook.io/biodata-catalyst-documentation/')
    post_svg(system=system,
             subsystem=subsystem,
             ok=response.ok)
    post_svg(system=system,
             subsystem='overall',
             ok=response.ok)


def post_gen3_svgs():
    system = 'gen3'
    url = "https://gen3.biodatacatalyst.nhlbi.nih.gov/"
    if getuser() == 'quokka':
        auth = Gen3Auth(endpoint=url, refresh_file=os.path.expanduser("~/.credentials/gen3_credentials_oct_2020.json"))
    else:
        auth = Gen3Auth(endpoint=url, refresh_token=os.environ['GEN3_CREDS'])  # assume we're on gitlab

    all_subsystems_ok = True
    for subsystem, subsystem_client in [('System Heartbeat Check', Gen3Index)]:
        subsystem_ok = subsystem_client(url, auth_provider=auth).is_healthy()
        post_svg(system=system,
                 subsystem=subsystem,
                 ok=subsystem_ok)
        if not subsystem_ok:
            all_subsystems_ok = False

    subsystem = 'gen3.biodatacatalyst.nhlbi.nih.gov'
    main_site_response = requests.head('https://gen3.biodatacatalyst.nhlbi.nih.gov/')
    post_svg(system=system,
             subsystem=subsystem,
             ok=main_site_response.ok)
    if not main_site_response.ok:
        all_subsystems_ok = False

    post_svg(system=system,
             subsystem='overall',
             ok=all_subsystems_ok)


def post_status_to_big_query(system: str, subsystem: str, up: int, create = False):
    system = system.replace('-', '_').replace(' ', '_').replace('.', '_').lower()
    subsystem = subsystem.replace('-', '_').replace(' ', '_').replace('.', '_').lower()
    table_id = f'unc-renci-bdc-itwg.bdc.{system}_{subsystem}'
    row = {'u': up,
           'd': 1 if up == 0 else 0,
           'm': 0,
           't': str(datetime.datetime.now())}
    try:
        # Create if does not exist
        if create:
            schema = [
                bigquery.SchemaField('t', 'TIMESTAMP', mode='REQUIRED'),
                bigquery.SchemaField('u', 'INTEGER', mode='REQUIRED'),
                bigquery.SchemaField('d', 'INTEGER', mode='REQUIRED'),
                bigquery.SchemaField('m', 'INTEGER', mode='REQUIRED')
                ]
            table = bigquery.Table(table_id, schema=schema)
            try:
                table = client.create_table(table)
                log.info(f'Created table {table.project}.{table.dataset_id}.{table.table_id}')
            except Conflict:
                log.warning(f'Table {table.project}.{table.dataset_id}.{table.table_id} already exists')
                
        errors = client.insert_rows_json(table=table_id,
                                         json_rows=[row])
        if errors:
            print(f'Encountered errors while inserting rows: {errors}')
        else:
            print(f'Successfully posted to BigQuery DB: {table_id} (up: {up})')
    except Exception as e:
        log.exception(f'Error shipping the data to Big Query ({table_id}):')


def post_integration_test_svgs():
    system = 'integration_tests'
    ok = get_latest_pipeline_status()
    if ok == 'success':
        post_svg(system=system,
                 subsystem='overall',
                 ok=True)
    elif ok in ('failed', 'failure'):
        post_svg(system=system,
                 subsystem='overall',
                 ok=False)
    else:
        # ignore if still in "running" or "pending"; only happens if the entire returned page is this
        print(f'Integration Test status was: {ok}, delaying posting the svg.')


def post_seven_bridges_svgs():
    system = 'seven_bridges'
    all_subsystems_ok = True
    real_usage_response = requests.get('https://7jfj299y8cyp.statuspage.io/api/v2/summary.json')
    for component in real_usage_response.json()['components']:
        subsystem = component['name']
        if subsystem not in ('Login', 'Execution', 'API', 'Data Uploaders', 'Files', 'Billing'):
            log.warning(f'Unknown subsystem was added?  {subsystem}')
        status = True if component['status'] == 'operational' else False
        post_svg(system=system,
                 subsystem=subsystem,
                 ok=status)
        if not status:
            all_subsystems_ok = False
    real_usage_response = sevenbridges_realtime_status()
    for component in ('Login', 'API', 'Files', 'Billing'):
        status = real_usage_response[component]
        post_svg(system=system,
                 subsystem=f'{component}_live',
                 ok=status)
        if status is False:
            all_subsystems_ok = False
    post_svg(system=system,
             subsystem='overall',
             ok=all_subsystems_ok)


# def post_helx_svgs():
#     post_svg(system='helx',
#              subsystem='overall',
#              ok='Not Implemented Yet')


def post_pic_sure_svgs():
    response = requests.get('https://picsure.biodatacatalyst.nhlbi.nih.gov/picsure/system/status')
    real_usage_response = picsure_realtime_status()
    post_svg(system='pic_sure',
             subsystem='system_status',
             ok=response.text == 'RUNNING')
    if os.environ.get('PICSURE_AUTH_TOKEN'):
        post_svg(system='pic_sure',
                subsystem='usage_live',
                ok=real_usage_response)
        post_svg(system='pic_sure',
                subsystem='overall',
                ok=real_usage_response and response.text == 'RUNNING')
    else:
        post_svg(system='pic_sure',
                subsystem='overall',
                ok=response.text == 'RUNNING')

def post_pic_sure_without_login_svgs():
    response = requests.get('https://openpicsure.biodatacatalyst.nhlbi.nih.gov/picsure/system/status')
    # real_usage_response = picsure_realtime_status()
    post_svg(system='pic_sure_without_login',
             subsystem='system_status',
             ok=response.text == 'RUNNING')


def post_ras_svg():
    # We certainly don't need all of these fields, but I'm keeping them to
    # document what's available
    fields = ('info;cur;24h.uptime;24h.status;last.date;world.id;world.score;'
              'world.uptime;hourly.period.from;hourly.uptime;daily.period.from;'
              'daily.period.tz;daily.uptime;daily.status;daily.avg')
    try:
        response = requests.get(f'https://mongocache.asm.saas.broadcom.com/'
                                f'synth/current/63160/monitor/537680/?fields={fields}')
        ok = response.json()['result'][0]['cur']['status'] == 0
        # Status explained:
        # - 0: Operating normally
        # - 1: Performance issues
        # - 2: Service disruption
    except Exception:
        log.exception('Failed to extract RAS response')
        ok = 'unknown'
    post_svg(system='ras',
             subsystem='overall',
             ok=ok)


def picsure_realtime_status():
    """Actually use PIC-SURE."""
    # Available projects (May 4, 2021):
    # | 02e23f52-f354-4e8b-992c-d37c8b9ba140
    # | 70c837be-5ffc-11eb-ae93-0242ac130002
    #
    # Based on: https://github.com/hms-dbmi/pic-sure-python-client
    #      and: https://terra.biodatacatalyst.nhlbi.nih.gov/#workspaces/biodata-catalyst/BioData%20Catalyst%20PIC-SURE%20API%20Python%20examples/notebooks
    token = os.environ['PICSURE_AUTH_TOKEN']
    domain = 'https://picsure.biodatacatalyst.nhlbi.nih.gov/picsure'
    resource_id = '02e23f52-f354-4e8b-992c-d37c8b9ba140'
    try:
        client = PicSureClient.Client()
        connection = client.connect(domain, token)
        adapter = PicSureHpdsLib.Adapter(connection)
        resource = adapter.useResource(resource_id)
        copdgene_data = resource.dictionary().find("Genetic Epidemiology of COPD (COPDGene)").DataFrame()
        header_seen = 'Genetic Epidemiology of COPD (COPDGene)' in str(copdgene_data.index)
        ## last line looks like: "[353 rows x 7 columns]"; parse this to determine a non-zero # of rows
        # rows_are_non_zero = int(str(copdgene_data).split('\n')[-1].split(' ')[0][1:]) > 0
        return True  # and rows_are_non_zero
    except Exception as e:  # if not authorized, this returns a KeyError
        print(f'Failed to get status from PIC-SURE:\n{e}')
        return False



def sevenbridges_realtime_status():
    """Actually use Seven Bridges."""
    expected_api_response = {"rate_limit_url": "https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2/rate_limit",
                             "user_url": "https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2/user",
                             "users_url": "https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2/users",
                             "billing_url": "https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2/billing",
                             "projects_url": "https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2/projects",
                             "files_url": "https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2/files",
                             "tasks_url": "https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2/tasks",
                             "apps_url": "https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2/apps",
                             "action_url": "https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2/action",
                             "upload_url": "https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2/upload",
                             "storage_url": "https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2/storage",
                             "markers_url": "https://api.sb.biodatacatalyst.nhlbi.nih.gov/v2/genome/markers"}
    sb_status = {'Login': 'unknown',
                 # 'Execution': 'unknown',
                 'API': 'unknown',
                 # 'Data Uploaders': 'unknown',
                 'Files': 'unknown',
                 'Billing': 'unknown'}

    try:
        response = requests.get(os.environ['SB_API_ENDPOINT'])
        response.raise_for_status()
        if response.json() != expected_api_response:
            log.warning(f'API seems to have returned an unexpected response (and may have been updated): '
                        f'{json.dumps(response.json(), indent=4)}')
        sb_status['API'] = True
        print('SB API use returned successfully.')
    except Exception as e:
        log.exception('API use failed.')
        sb_status['API'] = False

    try:
        api = sbg.Api(advance_access=True)
        assert 'mborsellino/test' in [p.id for p in api.projects.query().all() if p.id == 'mborsellino/test']
        sb_status['Login'] = True
        print('SB Login returned successfully.')
    except Exception as e:
        log.exception('SB Login use failed.')
        sb_status['Login'] = False
        return sb_status

    try:
        bg = api.billing_groups.query(limit=1)[0]
        print('Billing query returned successfully.')
        sb_status['Billing'] = True
    except Exception as e:
        log.exception('Billing query failed.')
        sb_status['Billing'] = False
        return sb_status

    # create test file
    test_file_name = 'test.txt'
    test_file_path = os.path.abspath(test_file_name)
    with open(test_file_path, 'w') as f:
        f.write('nothing to see here')
    # this file doesn't exist yet and will be made when we download test_file_name from the project after upload
    downloaded_test_file_path = os.path.abspath(f'downloaded_{test_file_name}')

    try:
        # create project
        project = api.projects.create(name=str(uuid.uuid4()), billing_group=bg.id)
        print(f'Creating project: {project}')
        try:
            files = api.files.query(project=project)
            log.info(f' - Fresh project should have 0 files: {files}')
            log.info(f' - Uploading: {test_file_path}')
            upload = api.files.upload(test_file_path, project, file_name=test_file_name)
            upload.wait()
            files = api.files.query(project=project)
            log.info(f' - Project should now have 1 file: {files}')
            my_file = [file for file in files if test_file_name == file.name][0]
            file_id = api.files.get(my_file.id)
            file_id.download(downloaded_test_file_path)
            assert os.path.exists(downloaded_test_file_path)
            log.info(f' - File downloaded successfully: {downloaded_test_file_path}')
            log.info('File upload/download to project returned successfully.')
            sb_status['Files'] = True
        except Exception as e:
            log.exception('File upload/download to project failed.')
            sb_status['Files'] = False
            return sb_status
    finally:
        print(f' - Removing {test_file_path} and {downloaded_test_file_path}')
        for f in [test_file_path, downloaded_test_file_path]:
            if os.path.exists(f):
                os.remove(f)
        p = api.projects.get(id=project)
        print(f' - Deleting project: {p}')
        p.delete()
    return sb_status


def poll_endpoints():
    for system in ('Terra', 'Dockstore', 'Seven Bridges', 'BioCat Documentation', 'Gen3', 'Integration Tests',
                   'HeLx', 'PIC-SURE', 'PIC-SURE-WO-LOGIN', 'Bond', 'Leonardo', 'RAS'):
        if system == 'Terra':
            post_terra_svgs()
        elif system == 'Dockstore':
            post_dockstore_svgs()
        elif system == 'Seven Bridges':
            post_seven_bridges_svgs()
        elif system == 'BioCat Documentation':
            post_biocat_documentation_svgs()
        elif system == 'Gen3':
            post_gen3_svgs()
        elif system == 'Integration Tests':
            # THIS NEEDS MODIFICATION WITH NEW SYSTEMS. RETURN TRUE FOR NOW
            pass
            # post_integration_test_svgs()
        elif system == 'HeLx':
            pass
#             post_helx_svgs()
        elif system == 'PIC-SURE':
            post_pic_sure_svgs()
        elif system == 'PIC-SURE-WO-LOGIN':
            post_pic_sure_without_login_svgs()
        elif system == 'Bond':
            post_bond_svgs()
        elif system == 'Leonardo':
            post_leonardo_svgs()
        elif system == 'RAS':
            post_ras_svg()
        else:
            raise NotImplementedError(f'Unknown system: {system}')
#     post_time_svg()


def poll_infinitely():
    timing = 60 * 2
    while True:
        poll_endpoints()
        print(f'Polling infinitely every {timing}s.')
        time.sleep(timing)


def main():
    poll_endpoints()


if __name__ == '__main__':
    main()
