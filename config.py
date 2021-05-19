#Application configuration File
################################

#Secret key that will be used by Flask for securely signing the session cookie
# and can be used for other security related needs
SECRET_KEY = 'SECRET_KEY'

#Directory To Watch, If not specified, the following value will be considered explicitly.
WATCH_DIRECTORY = "C:\\SCRIPTS"

#Delay Between Watch Cycles In Seconds
WATCH_DELAY = 1

#Check The WATCH_DIRECTORY and its children
WATCH_RECURSIVELY = False

#Patterns of the files to watch
WATCH_PATTERN = ('.txt','.trc','.log')

#Map to the REDIS Server Port
BROKER_URL = 'redis://localhost:6379'

#Patterns for observations
EXCEPTION_PATTERN = ['Exception', 'Fatal', 'Error']