import os
import requests
import datetime
from CloudFlare import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError
from dotenv import load_dotenv

load_dotenv()
email = os.getenv('EMAIL')
key = os.getenv('KEY')
certtoken = os.getenv('CERTTOKEN')
domain = os.getenv('DOMAIN')

def getIp():
    return requests.get('http://ipv4.icanhazip.com').text

def updateRecord(cf: CloudFlare, dns_record: dict, zone: dict):
    """ updateRecord function.
        This function updates a record on the CloudFlare instance.
    """
    # Some basic information
    dns_record_id = dns_record['id']
    dns_name = dns_record['name']
    zone_id = zone[0]['id']
    proxied_record = dns_record['proxied']
    old_ip = dns_record['content']
    old_ip_type = dns_record['type']

    # Quick sanity to check to make sure that we're not needlessly wasting data doing an update.
    sanity_check = old_ip not in getIp()
    if sanity_check:

        dns_record = {
            'type': old_ip_type,
            'content': getIp(),
            'name': dns_name,
            'proxied': proxied_record
        }
        # Hey look! Some error checking for a change.
        try:
            cf.zones.dns_records.put(zone_id, dns_record_id, data=dns_record)
        except CloudFlareAPIError as e:
            exit(f'/zones.dns_records.put {dns_name} - {e}{e} - api error')
        print(f'Updated DDNS {dns_name} points to {getIp()}')

def main():
    """ Main entrypoint for utility.

    Connects to the CloudFlare service, Checks the A records
    for a specified zone, if the IP of that record is different
    than your current public IP it runs the updateRecord function.
    """
    # Connect to CloudFlare service.
    cf = CloudFlare(email=email, key=key, certtoken=certtoken)
    # Pick the zone to use
    zone = cf.zones.get(params={'name': domain})
    # Get all records for that zone.
    dns_records = cf.zones.dns_records.get(zone[0]['id'])
    # Loop through all those records
    for record in dns_records:
        if record['type'] == 'A':
            # Print some information for logging since all output is going to be
            # redirected into a log file, in my usecase anyways.
            print(datetime.datetime.now())
            print(f'Current stored IP: {record["content"]}')
            print(f'Current public IP: {getIp()}')
            # Check if the current public IP matches the currently stored
            # IP Address if so, nothing to do, if not update the record.
            if record['content'] in getIp():
                print("Match, no need to update")
            else:
                print("Updating Record..")
                updateRecord(cf, record, zone)


if __name__ == "__main__":
    main()