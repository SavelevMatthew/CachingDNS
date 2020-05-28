# CachingDNS

This utility realise Redirecting DNS Server with Cache function, so when DNS request incomes, it will look for answers in cache first and then if nothing was found will ask for help parent DNS server

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the following packages.

```bash
pip install -r requirements.txt
```

## Configuration

Open **config.ini** file to set up, then change following setting if you want:

ip - IP of your server, leave it 127.0.0.1 if you want to use localhost

port - don't recommend to change it, since DNS requests are usually use 53th port to communicate

max_packet_size - maximal size of a packet, which can be received (RFC says max is 512 bytes, so we dont recommend setting up less amount)

parent_dns - IP of parent DNS (8.8.8.8 by default, which is Google Developer's DNS)

cache_filename - Name of the file, where all cache information will be stored

## Launching

#### Mac OS / Linux

```bash
sudo python main.py
```
Make sure you run it in sudo, since running server on a port, which are less than 80, requires your permissions

#### Windows
**Run cmd as ADMINISTRATOR**
```bash
python main.py
```

## Usage

Use whatever utility you want to send DNS requests...Here is few "default" examples

#### Mac OS / Linux

```bash
dig example.com @127.0.0.1
```

#### Windows
```bash
nslookup example.com 127.0.0.1
```

## Author
###  Savelev Matvey

e-mail: savelevmatthew@gmail.com

##### GitHub: [@SavelevMatthew](https://github.com/SavelevMatthew)
