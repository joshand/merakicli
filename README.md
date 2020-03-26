# merakicli

Meraki Dashboard CLI (highly experimental). Only a few bits of basic functionality for now!
Designed to give you that Cisco IOS "look and feel" for the Meraki Dashboard.

## Summary

## Usage

$ python3 cli.py 
Welcome to the Meraki shell. Type help or ? to list commands.

```
# ?                                                                                                                                                                         
  context         change to the specified context             
  exit            exit the program                            
  quit            exit the program                            
  end             exit to root context                        
  no              negate a command                            
  show            show information for a given object         
  organization    enter the context of a specific organziation

# sho org | inc cisco                                                                                                                                                       
#   Organization ID     Organization Name                 
3   854984              Cisco Cloud Calling/Meraki/MPP Org
4   882332              Cisco Meraki
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
