# Pulse Robotic Arm Visual Components Integration
This repo contains all needed resources to integrate [Pulse](https://rozum.com/robotic-arm/) into [Visual Components](https://www.visualcomponents.com/).
## Contents:
* Arm model with `.vcmx` extension.
* Post processor that translates the code writen in Visual Components into production-ready script that could be run on real robot. Could be found in `RobotPostProcessor` folder.

## Installation:
Download this repo and follow the instructions below.

### Model (.vcmx file):
_Note:_ Visual Components have already integrated our model into their product line. But we're currently in active development process, so the latest version of model is located here.

Copy the model file into Visual Components **models directory**, the path is depending on your installation settings and should look like this: `C:\Users\%username%\My Documents\Visual Components\4.0\My Models\`.
Now robot model should appear in `My Models` section in Visual Components.

### Post Processor:
Move the `RobotPostProcessor` into `My Commands` directory. Its location is depending on your installation settings and should look like this: `C:\Users\%username%\My Documents\Visual Components\4.0\My Commands\`.
Then restart Visual Components and navigate to the **Programming** tab. PostProcess button must appear in the left corner of the toolbar. Use it when you need to get the code that should be run on real robot. It will generate Python script that should be used in combination with our [Python REST api](https://github.com/rozum-robotics/pulse-rest-python). 