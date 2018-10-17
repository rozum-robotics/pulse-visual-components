from vcCommand import *
import vcMatrix, os.path, math


def writeSetProperty(output_file, statement):
  value_expression = statement.ValueExpression.strip()
  output_file.write(indentation * depth + "%s = %s\n" % (statement.TargetProperty, value_expression))


def writePrint(output_file, statement):
  output_file.write(indentation * depth + 'print("%s")\n' % statement.Message)


def writeIf(output_file, statement):
  global depth
  _condition = statement.Condition.strip()
  output_file.write(indentation*depth + "if %s:\n" % _condition)
  depth += 1
  if not statement.ThenScope.Statements:
    output_file.write(indentation*depth + "pass\n" )
  for s in statement.ThenScope.Statements:
    translator = statement_translators.get(s.Type, unknown)
    translator(output_file, s)
  depth -= 1
  output_file.write(indentation*depth + "else:\n")
  depth += 1
  if not statement.ElseScope.Statements:
    output_file.write(indentation*depth + "pass\n" )
  for s in statement.ElseScope.Statements:
    translator = statement_translators.get(s.Type, unknown)
    translator(output_file, s)
  depth -= 1
  output_file.write(indentation*depth + "# end if\n")


def writeReturn(output_file, statement):
  output_file.write(indentation * depth + "return\n")


def writeHalt(output_file, statement):
  output_file.write(indentation * depth + "robot.freeze()\n")


def writeContinue(output_file,statement):
  output_file.write(indentation*depth + "continue\n")


def writeBreak(output_file,statement):
  output_file.write(indentation*depth + "break\n")


def writeWhile(output_file,statement):
  global depth
  _condition = statement.Condition.strip()
  output_file.write(indentation * depth + "while %s:\n" % _condition )
  depth += 1
  if not statement.Scope.Statements:
    output_file.write(indentation*depth + "pass\n" )
  for s in statement.Scope.Statements:
    translator = statement_translators.get(s.Type, unknown)
    translator(output_file,s)
  depth -= 1
  output_file.write(indentation*depth + "# end while\n")


def writeWaitBin(output_file, statement):
  unknown(output_file, statement)


def writeSetBin(output_file, statement):
  if statement.OutputPort == GRIPPER_PORT:
    if statement.OutputValue:
        output_file.write(indentation * depth + "robot.open_gripper()\n")
    else:
        output_file.write(indentation * depth + "robot.close_gripper()\n")
  else:
    port = statement.OutputPort
    if statement.OutputValue:
      output_file.write(indentation * depth + "robot.set_digital_output_high(%d)\n" % port)
    else:
      output_file.write(indentation * depth + "robot.set_digital_output_low(%d)\n" % port)

def writeDelay(output_file, statement):
  output_file.write(indentation*depth + "time.sleep(%.3f)\n" % statement.Delay)


def writeComment(output_file, statement):
  output_file.write(indentation*depth + "# %s\n" % statement.Comment)


def writeCall(output_file, statement):
  if statement.getProperty("Routine").Value:
    output_file.write(indentation*depth + "%s(robot) #subroutine call\n" % statement.getProperty("Routine").Value.Name )


def writeLinMotion(output_file, statement):
  joint_values = statement.Positions[0].JointValues
  joint_values_str = ','.join(map(str, joint_values))
  output_file.write(indentation*depth + "robot.set_pose(Pose([" + joint_values_str + "]), %f, MotionType.LINEAR)\n" % (clamp(statement.JointSpeed * 100, 1, 100)))
  output_file.write(indentation*depth + "robot.await_motion()\n")



def writePtpMotion(output_file, statement):
  joint_values = statement.Positions[0].JointValues
  joint_values_str = ','.join(map(str, joint_values))
  output_file.write(indentation*depth + "robot.set_pose(Pose([" + joint_values_str + "]), %f, MotionType.JOINT)\n" % (clamp(statement.JointSpeed * 100, 1, 100)))
  output_file.write(indentation*depth + "robot.await_motion()\n")


def writePath(output_file, statement):
  output_file.write(indentation * depth + "# <START PATH: %s>\n" % (statement.Name))
  motiontarget.JointTurnMode = VC_MOTIONTARGET_TURN_NEAREST
  motiontarget.TargetMode = VC_MOTIONTARGET_TM_NORMAL
  motiontarget.MotionType = VC_MOTIONTARGET_MT_LINEAR
  poses = []
  max_speed = 0
  for i in range(statement.getSchemaSize()):
    target = statement.getSchemaValue(i, "Position")
    motiontarget.Target = target
    joint_values = motiontarget.JointValues
    motiontarget.JointValues = joint_values
    joint_values_str = ','.join(map(str, joint_values))
    pose = "Pose([" + joint_values_str + "])"
    speed = statement.getSchemaValue(i, "MaxSpeed") / 10
    max_speed = clamp(max(max_speed, speed), 0, 100)
    poses.append(pose)
  output_file.write(indentation * depth + "robot.run_poses([" + ",".join(poses) + "], %f, MotionType.LINEAR)\n" % (max_speed))
  output_file.write(indentation * depth + "robot.await_motion()\n")
  output_file.write(indentation * depth + "# <END PATH: %s>\n" % (statement.Name))


def unknown(output_file, statement):
  print '> Unsupported statement type skipped:', statement.Type
  output_file.write(indentation * depth + "print('> Unsupported statement type skipped: %s')" % statement.Type)


def translateRoutine(routine, name, output_file):
  global depth
  output_file.write("def %s(robot):\n" % name)
  depth = 1
  pointCount = 0
  statementCount = 0
  for statement in routine.Statements:
    translator = statement_translators.get(statement.Type, unknown)
    translator(output_file,statement)
  output_file.write("# end %s\n\n" % name)
  output_file.write("\n")


def postProcess(app, program, uri):
  global motiontarget
  head, tail = os.path.split(uri)
  mainName = tail[:len(tail)-3]
  motiontarget = program.Executor.Controller.createTarget()
  with open(uri, "w") as output_file:
    translateRoutine(program.MainRoutine, mainName, output_file)
    # subroutines
    for routine in program.Routines:
      translateRoutine(routine, routine.Name, output_file)
    output_file.write("%s(robot)\n" % mainName)
    return True,[uri]
  return False,[uri]


GRIPPER_PORT = 101
indentation = '\t'
statement_translators = {
VC_STATEMENT_SETPROPERTY:writeSetProperty,
VC_STATEMENT_PRINT:writePrint,
VC_STATEMENT_IF:writeIf,
VC_STATEMENT_RETURN:writeReturn,
VC_STATEMENT_HALT:writeHalt,
VC_STATEMENT_CONTINUE:writeContinue,
VC_STATEMENT_BREAK:writeBreak,
VC_STATEMENT_WHILE:writeWhile,
VC_STATEMENT_WAITBIN:writeWaitBin,
VC_STATEMENT_SETBIN:writeSetBin,
VC_STATEMENT_DELAY:writeDelay,
VC_STATEMENT_COMMENT:writeComment,
VC_STATEMENT_CALL:writeCall,
VC_STATEMENT_LINMOTION:writeLinMotion,
VC_STATEMENT_PTPMOTION:writePtpMotion,
VC_STATEMENT_PATH:writePath}


def clamp(val, min_val, max_val):
  return max(min(val, max_val), min_val)
