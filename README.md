# merakicli

Meraki Dashboard CLI (highly experimental). Only a few bits of basic functionality for now!
Designed to give you that Cisco IOS "look and feel" for the Meraki Dashboard.

## Summary

## Usage

```
$ python3 cli.py 
Welcome to the Meraki shell. Type help or ? to list commands.

# ?                                                                                                                                                                         
  context         change to the specified context             
  exit            exit the program                            
  quit            exit the program                            
  end             exit to root context                        
  no              negate a command                            
  show            show information for a given object         
  organization    enter the context of a specific organziation

# sho ?   
  debug            show debug information    
  organizations    show list of organizations

# sho or?
organizations

# sho org ?
  |       Output modifiers
  <cr>                    

# sho org | ?
  begin      Begin with the line that matches
  exclude    Exclude lines that match        
  include    Include lines that match     

# sho org | inc cisco                                                                                                                                                       
#   Organization ID     Organization Name                 
3   854984              Cisco Cloud Calling/Meraki/MPP Org
4   882332              Cisco Meraki

# con Org-Josh Anderson/Net-Josh Anderson                                                                                                                                   
Org-Josh Anderson/Net-Josh Anderson# sho dev                                                                                                                                
#   Serial #        Model       MAC Address        WAN 1         WAN 2         LAN             Name         
3   Q2UY-XXXX-XXXX  MG21        2c:3f:0b:01:05:6d                              192.168.128.6                
4   Q3AB-XXXX-XXXX  MR56        68:3a:1e:ff:f8:6d                              192.168.128.9   Anderson W 56
5   Q3AB-XXXX-XXXX  MR56        68:3a:1e:ff:f9:2f                              192.168.128.2   Anderson E 56
6   Q2MP-XXXX-XXXX  MS220-48LP  88:15:44:cf:56:1d                              192.168.128.8   Mgmt Switch  
7   Q2HP-XXXX-XXXX  MS220-8P    00:18:0a:7d:57:a8                              192.168.128.35  Office       
8   Q2EW-XXXX-XXXX  MS350-24X   34:56:fe:1e:55:60                              192.168.128.13  Switch W     
9   Q2EW-XXXX-XXXX  MS350-24X   0c:8d:db:bc:76:a0                              192.168.128.10  Switch E     
10  Q3EA-XXXX-XXXX  MS390-24    98:18:88:00:a5:80                              192.168.128.3                
11  Q2PV-XXXX-XXXX  MV32        68:3a:1e:00:fc:e0                              192.168.128.12  Closet       
12  Q2JV-XXXX-XXXX  MV72        68:3a:1e:00:89:58                              192.168.128.22  Front Walk   
13  Q2JV-XXXX-XXXX  MV72        68:3a:1e:00:89:5e                              192.168.128.11  Back Deck    
14  Q2MY-XXXX-XXXX  MX68CW-NA   ac:17:c8:8f:88:d0  11.22.111.22  172.31.128.4  11.22.111.22
```

## Running
```shell script
git clone https://github.com/joshand/merakicli.git
pip3 install -r requirements.txt
mv _config_sample.py _config.py
```
Edit the config file to include your preferences (add API key)
```shell script
python3 cli.py
```
