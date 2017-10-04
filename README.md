# glpi_sync
[Check_MK](https://mathias-kettner.de/check_mk.html) extension to synchronize information from [GLPI](http://www.glpi-project.org/).

### How it works
This extension makes a cron job that connects to the GLPI database, queries information on computers and synchronizes it with hosts' attributes in Check_MK. It can add new hosts to Check_MK. It can also run an inventory on new hosts.

### Cron job
Check_MK's internal cron is used to run this job. A user with admin role can also run this job manually.

### Synchronized attributes
* criticality, such as prod, uat or dev,
* physical or virtual computer,
* operating system.

### Requirements
* Check_MK 1.4.0,
* GLPI 0.84 or newer.
