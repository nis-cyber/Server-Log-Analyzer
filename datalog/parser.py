import re
import csv
from multiprocessing import Pool
import geoip2.database

# Load the GeoIP database
geoip_reader = geoip2.database.Reader(
    '/Users/nishantkharel/Downloads/GeoLite2-Country_20240105/GeoLite2-Country.mmdb')


def get_country_from_ip(ip):
    try:
        response = geoip_reader.country(ip)
        country = response.country.iso_code
        return country
    except geoip2.errors.AddressNotFoundError:
        return 'Unknown'


def parse_log_line(line):
    pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.+?)\] ".+?" \d+ \d+ "(.*?)" "(.*?)"'
    match = re.search(pattern, line)
    if match:
        ip = match.group(1)
        date_time = match.group(2)
        user_agent = match.group(4)

        browser_match = re.search(r'(?:^|/)(\w+)(?:/|\s)', user_agent)
        browser = browser_match.group(1) if browser_match else 'Unknown'

        if 'Linux' in user_agent:
            os = 'Linux'
        elif 'Windows' in user_agent:
            os = 'Windows'
        elif 'Mac OS' in user_agent:
            os = 'Mac OS'
        else:
            os = 'Other'

        country = get_country_from_ip(ip)

        return ip, browser, os, date_time, country
    else:
        return None


def parse_log_file(filename):
    ip_list = []
    with open(filename) as f:
        pool = Pool()
        ip_list = pool.map(parse_log_line, f)
        pool.close()
        pool.join()
    return [item for item in ip_list if item is not None]


def write_to_csv(data):
    with open('output.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['IP', 'Browser', 'Operating System', 'Date Time', 'Country'])
        writer.writerows(data)


if __name__ == "__main__":
    ip_data = parse_log_file('/Users/nishantkharel/Documents/6th Semester /dpc/datalog/generated_log_data')
    write_to_csv(ip_data)
