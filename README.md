**The Davis Weather Station Receiver for the Raspberry Pi works without a display / without the console. The Pi is equipped with an RFM69 radio module, which directly receives the data.**

**Software Components**  
There are two software components: A program that processes the data from the radio module and writes weather station data to a MySQL database (`davislogger.py`). The second component is a new driver for Weewx, which reads the data from the MySQL database, formats it for Weewx, and passes it on.

---

**Installation**

1. Install Weewx with webserver and mariaDB
 - official instructions: For example, on a Raspberry Pi: [Weewx Installation Guide](https://www.weewx.com/docs/5.1/quickstarts/debian/#installation-on-debian-systems) (During setup, it will ask for the hardware; choose the Simulator first).
 - Install a web server: `sudo apt-get install apache2` After installation, the page can be accessed via: `http://ipaddress/weewx/`
 - Install MariaDB: `sudo apt install mariadb`
 - Set Weewx to use MySQL: [Weewx MySQL Setup Guide](https://www.weewx.com/docs/5.1/usersguide/mysql-mariadb/). Adjust the configuration file accordingly: `nano /etc/weewx/weewx.conf`
 - Next, create the database: `weectl database create` More info: [Weewx Database Command](https://www.weewx.com/docs/5.1/utilities/weectl-database/)

2. Receive data from the Davis weatherstaion
 - Install your RFM69 receiver
 - Activate the SPI interface `sudo raspi-config`, go to interfaces, then SPI, and enable it. Restart the system.
 - Clone this repository: `git clone https://github.com/simsasaile/davislogger.git` to your home folder.
 - Install libraries: `sudo apt-get install python3-pymysql` and `sudo apt install python3-numpy`
 - If a ready-made RFM module for the Pi has been purchased, you may need to adjust `IRQ_PIN` in `davisreceiver.py`.
 - To ensure the davislogger starts automatically with every Pi boot, adjust the user and paths in the `davislogger.service` file and copy it to: `sudo cp davislogger.service /etc/systemd/system/`
 - Enable the service with: `sudo systemctl enable davislogger.service` and start it with: `sudo systemctl start davislogger.service`. To check the status of the service, use: `sudo systemctl status davislogger.service`
 - Copy the driver for davislogger into Weewx: `sudo cp /home/pi/davislogger/vueiss.py /usr/share/weewx/weewx/drivers/`
 - Select the new driver: `weectl station reconfigure` and check if everything is okay: `sudo systemctl status weewx`

Now everything should be working. Data should arrive and be displayed on the website.
