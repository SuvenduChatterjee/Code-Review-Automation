# Code-Review-Automation
## Sort overview
This solution checks OO code(Java) against pre-defined violation matrix (consists of set of rules defined in configuration file). Utility is built by using python and utilizes flask framework for web hosting. OO content pack is uploaded as input to utility which contains code and their dependencies. Utility will parse the given content pack by identifying and extracting the Flows and Configuration items as objects. These objects are validated against defined rules and coding standards. After validation, a detailed report is generated, which contains dashboard and details of error and warning. Report can be downloaded as PDF or xls format.

## Process Diagram
![image](https://user-images.githubusercontent.com/47567642/180967746-14d0aee1-2ae6-4381-8c60-abbae2ae22c4.png)

To know more checkout the docs...
