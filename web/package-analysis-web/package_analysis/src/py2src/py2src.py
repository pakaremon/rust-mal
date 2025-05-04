from py2src.url_finder import  GetFinalURL


from argparse import ArgumentParser,ArgumentTypeError
import logging, coloredlogs
import os, pathlib
import json



class Py2srcApplication():
  
  @staticmethod
  def __packageType(package):
    if len(package.split(":")) >2:
      raise ArgumentTypeError("Invlaid package name ")
    return package
  
  @staticmethod
  def __logLevelType(x):
    x = int(x)
    if x==0:
      return 100
    elif x==1:
      return logging.CRITICAL
    elif x==2:
      return logging.ERROR
    elif x==3:
      return logging.WARNING
    elif x==4:
      return logging.INFO
    elif x==5:
      return logging.DEBUG
    else:
      raise ArgumentTypeError("Log level must be between 0 and 5")
  
  def __init__(self):
    parser = ArgumentParser()

    parser.add_argument(
      'package', 
      type=str,
      help='Package name can be in the form <package_name>:<package_version>. If no version is specified the latest version is retrieved.'
    )
    # add argument for ecosystem
    parser.add_argument(
      '-e', '--ecosystem',
      type=str,
      default="pypi",
      help='Ecosystem name. default(pypi), options: pypi, npm',
    )
    parser.add_argument(
      '-lv', '--loglevel',
      type=Py2srcApplication.__logLevelType,
      default=logging.INFO,
      help='Log level. From 0(no log) to 5(debug). default(3)',
    )



    args = parser.parse_args()

    l=logging.getLogger("pys2src")
    coloredlogs.install(logger=l,level=args.loglevel)
    
    
    rl=logging.getLogger("py2src_report")
    rl.setLevel(logging.DEBUG) 


    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(CustomFormatter())
    rl.addHandler(ch)

    try:
      
      pakage=args.package.split(":")
      package_name=pakage[0]
      package_version=pakage[1] if len(pakage)==2 else None
      ecosystem=args.ecosystem
      
      current_folder=pathlib.Path().resolve()
      url_data = GetFinalURL(package_name, ecosystem=ecosystem).get_final_url()
      github_url = url_data[0]
      print("Package name: ", package_name, "Github URL: ", github_url)
      

        
    except Exception as e:
      import traceback
      l.critical("Exception in main code: {}\n{}".format(e,traceback.format_exc()))


class CustomFormatter(logging.Formatter):

    white= "\u001b[37m"
    grey = "\x1b[38;21m"
    green = "\u001b[32m"
    orange = "\u001b[35m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    
    format = "Lastymile Report: %(message)s"

    FORMATS = {
        logging.DEBUG: white + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

if __name__ == "__main__":
    Py2srcApplication()
  

    

  