from vcApplication import *

def OnStart():
  cmduri = getApplicationPath() + 'PostProcessLauncher.py'
  cmd = loadCommand('PostProcessLauncher',cmduri)
  addMenuItem('VcTabTeach/Export', "Post Process", -1, "PostProcessLauncher")
