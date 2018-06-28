from vcCommand import *
import os, importlib
'''
a = importlib.import_module( 'Translators.ABB_mod' )
print 'a',a
b = __import__( 'ABB_mod' )
print 'b',b
'''
app = getApplication()
translators_dir_name = 'Translators'



def firstState():
  program = getProgram()
  if not program:
    app.messageBox("No program selected, aborting.","Warning",VC_MESSAGE_TYPE_WARNING,VC_MESSAGE_BUTTONS_OK)
    return    
  controller = program.Executor.Controller
  cmd_uri = getCommandPath() # this command's uri
  cmd_uri = cmd_uri[8:] # remove "file:///" header
  cmdfolder, cmdfilename = os.path.split(cmd_uri)
  controller_filetype_map = read_controller_filetype_map(cmdfolder)
  file_filters = {}
  post_processors = {}
  translators_folder = os.path.join(cmdfolder, translators_dir_name)
  for root, folder, filenames in os.walk( translators_folder ):
    for filename in filenames:
      filebasename, extension = os.path.splitext(filename)
      if extension != '.py':
        continue # skip non python files
      if '__init__' in filename:
        continue # skip the __init__.py file
      post_uri = os.path.join(cmdfolder, filename) 
      tokens = filebasename.split('_')
      if len(tokens) < 2:
        # postprocessor name example:  test.py => "test Robot Program file (*.test)|*.test"
        manuf, filetype = tokens[0], tokens[0]
      else:
        # postprocessor name example:  ACME_obd.py => "ACME Robot Program file (*.obd)|*.obd"
        manuf, filetype = tokens[-2], tokens[-1]
      # import postprocessor module (and reload to allow easy editing)
      module_name = translators_dir_name + '.' + filebasename
      post_processor_module = importlib.import_module( module_name )
      post_processor_module = reload(post_processor_module)
      # dictionary of post processors per filetype
      post_processors['.'+filetype] = post_processor_module
      # file filter for this post processor
      file_filters[filetype] = "%s Robot Program file (*.%s)|*.%s" % (manuf, filetype, filetype)
  if not post_processors:
    print 'No post processors found! Please add a post processor file to "%s"' % (cmdfolder)
    return
  # try to find a specific filetype for this robot
  manuf_specific_filetype = controller_filetype_map.get(controller.Name, None)
  if manuf_specific_filetype and manuf_specific_filetype in file_filters:
    # matching post processor for this robot was found, allow using only that one
    file_filter = file_filters[manuf_specific_filetype]
  else:
    # matching processor not found or not known, allow using any post processor
    file_filter = '|'.join(file_filters.values())
  # ask file from the user
  uri = ""
  ok = True
  savecmd = app.findCommand("dialogSaveFile")
  savecmd.execute(uri,ok,file_filter,'Choose File to save Robot Program file')
  if not savecmd.Param_2:
    print "No file selected, aborting command."
    return
  uri = savecmd.Param_1
  fileuri = uri[8:]
  filebase, filetype = os.path.splitext(fileuri)
  # call the post processor that matches with the file type chosen by the user
  succesful, created_filenamelist = post_processors[filetype].postProcess(app, program, fileuri)
  if succesful:
    print 'Succesfully saved files:'
    for f in created_filenamelist:
      print '- %s' % f
  else:
    print 'File writing failed'
  program.Executor.Controller.clearTargets()


def getProgram():
  teachcontext = app.TeachContext
  if teachcontext.ActiveRobot:
    executors = teachcontext.ActiveRobot.findBehavioursByType(VC_ROBOTEXECUTOR)
    if executors:
      return executors[0].Program
  return None


def read_controller_filetype_map(cmdfolder):
  # add robot_controller_name / robot_program_filetype pairs 
  # to 'controllername_translator_map.txt' -file to force a specific post-processor for a certain robot brand
  controller_filetype_map = {}
  map_uri = os.path.join(cmdfolder, 'controllername_translator_map.txt')
  with open(map_uri,"r") as map_file:
    map_content = map_file.read()
    for line in map_content.split('\n'):
      cells = [x.strip() for x in line.split(',')]
      if len(cells) == 2 and all(cells):
        controller_filetype_map[cells[0]] = cells[1]
  return controller_filetype_map


addState( firstState )


