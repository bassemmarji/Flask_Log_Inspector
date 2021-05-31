#The Observer watches for any file change and then dispatches the respective events to an event handler.
from watchdog.observers import Observer
#The event handler will be notified when an event occurs.
from watchdog.events import FileSystemEventHandler
from flask_socketio import SocketIO
import time
import config
from checker import FileChecker
import datetime
import os, argparse

#If 1 switch the console version
console_version = False

if not console_version:
    # Setup and connect the socket instance to Redis Server
    socketio = SocketIO(message_queue=config.BROKER_URL)

# Sending Message through the websocket or directly to the console
def send_message(event, namespace, room, message):
    if not console_version:
        # print("Message = ", message)
        socketio.emit(event, {'msg': message}, namespace=namespace, room=room)
    else:
        print(message)

#Class that inherits from FileSystemEventHandler for handling the events sent by the Observer
class LogHandler(FileSystemEventHandler):

    def __init__(self,watchPattern,exceptionPattern,sessionid,namespace):
        self.sessionid = sessionid
        self.namespace = namespace
        self.watchPattern = watchPattern
        self.exceptionPattern = exceptionPattern
        #Instantiate the checker
        self.fc = FileChecker(self.exceptionPattern)

    def on_any_event(self, event):
        now = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")

        #To Observe files only not directories
        if not event.is_directory:
            #To cater for the on_move event
            path = event.src_path
            if hasattr(event, 'dest_path'):
                path = event.dest_path

            # Ensure that the file extension is among the pre-defined ones.
            if path.endswith(self.watchPattern):
               msg = f"{now} -- {event.event_type} -- File = {path}"
               #print("msg=", msg)

               if event.event_type in ('modified','created','moved'):
                  for type, msg in self.fc.checkForException(event=event, path=path):
                      send_message(event=type, namespace=self.namespace, room=self.sessionid, message=msg)
               else:
                  send_message(event='msg', namespace=self.namespace, room=self.sessionid, message=msg)

    def on_modified(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_created(self, event):
        pass

    def on_moved(self, event):
        pass

class LogWatcher:
    #Initialize the observer
    observer = None
    # Initialize the stop signal variable
    stop_signal = 0

    # The observer is the class that watches for any file system change and then dispatches the event to the event handler.
    def __init__(self, watchDirectory, watchDelay, watchRecursively,watchPattern,exceptionPattern,sessionid,namespace):
        # Initialize variables in relation
        self.watchDirectory = watchDirectory
        self.watchDelay = watchDelay
        self.watchRecursively = watchRecursively
        self.watchPattern = watchPattern
        self.exceptionPattern = exceptionPattern
        self.namespace = namespace
        self.sessionid = sessionid

        # Create an instance of watchdog.observer
        self.observer = Observer()
        # The event handler is an object that will be notified when something happens to the file system.
        self.event_handler = LogHandler(watchPattern,exceptionPattern,sessionid,namespace)

    def schedule(self):
        print("Observer Scheduled = ", self.observer.name)
        # Call the schedule function via the Observer instance attaching the event
        self.observer.schedule(self.event_handler, self.watchDirectory, recursive=self.watchRecursively)

    def start(self):
        print("Observer Started = ", self.observer.name)
        self.schedule()
        # Start the observer thread and wait for it to generate events
        now = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        msg = "Observer: {} - Started On: {} - Related To Session: {}".format(self.observer.name, now, self.sessionid)
        send_message(event='status', namespace=self.namespace, room=self.sessionid, message=msg)

        msg = "Watching {}: {} -- Folder: {} -- Every: {}(sec) -- For Patterns: {}".format( ('Recursively' if self.watchRecursively else 'Non-Recursively'), self.watchPattern,self.watchDirectory,self.watchDelay,self.exceptionPattern)
        send_message(event='status', namespace=self.namespace, room=self.sessionid, message=msg)
        self.observer.start()

    def run(self):
        print("Observer is running = ", self.observer.name)
        self.start()
        try:
            while True:
                time.sleep(self.watchDelay)

                if self.stop_signal == 1:
                   print("Observer stopped = ", self.observer.name , " stop signal =",self.stop_signal)
                   self.stop()
                   break
        except KeyboardInterrupt:
            self.stop()
        except:
            self.stop()
        self.observer.join()

    def stop(self):
        print("Observer Stopped = ", self.observer.name)

        now = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        msg = "Observer: {} - Stopped On: {} - Related To Session: {}".format(self.observer.name, now, self.sessionid)
        send_message(event='status', namespace=self.namespace, room=self.sessionid, message=msg)

        self.observer.stop()
        self.observer.join()

    def info(self):
        info = {
            'observerName':self.observer.name
           ,'watchDirectory':self.watchDirectory
           ,'watchDelay': self.watchDelay
           ,'watchRecursively':self.watchRecursively
           ,'watchPattern': self.watchPattern
        }
        return info

def is_dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise NotADirectoryError(path)

if __name__ == "__main__":
   console_version = True
   parser = argparse.ArgumentParser(description="Please enter the parameters...")
   parser.add_argument('--path'
                      ,default= config.WATCH_DIRECTORY
                      ,type=is_dir_path
                      ,help = "Enter the path for the folder to monitor")

   args = vars(parser.parse_args())

   if args['path']:
      print("The directory to monitor =",args['path'])

      logWatcher = LogWatcher(
         watchDirectory=args['path']
       , watchDelay=config.WATCH_DELAY
       , watchRecursively=config.WATCH_RECURSIVELY
       , watchPattern= config.WATCH_PATTERN
       , exceptionPattern=config.EXCEPTION_PATTERN
       , sessionid='Console'
       , namespace='/logWatcher'
       )
      logWatcher.run()


