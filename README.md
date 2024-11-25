**The Davis Weather Station Receiver for the Raspberry Pi works without a display / without the console. The Pi is equipped with an RFM69 radio module, which directly receives the data.**

**Software Components**  
There are two software components: A program that processes the data from the radio module and writes weather station data to a MySQL database (`davislogger.py`). The second component is a new driver for Weewx (vueiss.py), which reads the data from the MySQL database, and passes it to weewx.

The code is massivly based on the work of [buwx](https://github.com/buwx/logger). Therefore, a big thank you for that!

---

**Installation**

1. Install Weewx with webserver and mariaDB
 - official instructions: For example, on a Raspberry Pi: [Weewx Installation Guide](https://www.weewx.com/docs/5.1/quickstarts/debian/#installation-on-debian-systems) (During setup, it will ask for the hardware; choose the Simulator first).
 - Install a web server: `sudo apt-get install apache2` After installation, the page can be accessed via: `http://ipaddress/weewx/`
 - Install MariaDB: `sudo apt install mariadb-server` and a python database connector `sudo apt-get install python3-pymysql`
 - Set Weewx to use MySQL: [Weewx MySQL Setup Guide](https://www.weewx.com/docs/5.1/usersguide/mysql-mariadb/). Adjust the configuration file accordingly: `sudo nano /etc/weewx/weewx.conf` (Change **database = archive_sqlite** to **database = archive_mysql** under section [DataBindings])
 - Create user for weewx: Open MariaDb console: `sudo mariadb` and insert commands:
   ```
   CREATE USER 'weewx'@'localhost' IDENTIFIED BY 'weewx';
	GRANT select, update, create, delete, insert, alter, drop ON weewx.* TO weewx@localhost;
	```
	Schließe MariaDB console mit `exit`
 - Next create the new database: `sudo weectl database create` More info: [Weewx Database Command](https://www.weewx.com/docs/5.1/utilities/weectl-database/) and restart weewx `sudo systemctl restart weewx`

2. Receive data from the Davis Vantage weather station
 - Install your RFM69CW transceiver from HopeRF (https://buwx.de/index.php/technik/43-logger)
 - Activate the SPI interface `sudo raspi-config`, go to **3 Interface Options**, then **I4 SPI**, and enable it. Restart the system.
 - Install git `sudo apt install git` and clone this repository: `git clone https://github.com/simsasaile/davislogger.git` to your home folder.
 - Install libraries: `sudo apt install python3-numpy`
 - If a [ready-made RFM module](http://www.seegel-systeme.de/2015/09/02/ein-funkmodul-fuer-den-raspberry-raspyrfm/) for the Pi has been purchased, you may need to adjust `IRQ_PIN` in `logger/davisreceiver.py` to 22.
 - To ensure the davislogger starts automatically with every Pi boot, adjust the user and paths (ExecStart and WorkingDirectory) in the `davislogger.service` file and copy it to: `sudo cp davislogger.service /etc/systemd/system/`
 - Enable the service with: `sudo systemctl enable davislogger` and start it with: `sudo systemctl start davislogger`. To check the status of the service, use: `sudo systemctl status davislogger`
 - Copy the driver for davislogger into Weewx (you find it in the davislogger-folder): `sudo cp weewx_driver/vueiss.py /usr/share/weewx/weewx/drivers/`
 - Select the new driver: `weectl station reconfigure` Choose the driver "VueISS" and restart weewx `sudo systemctl restart weewx`. Check if everything is okay: `sudo systemctl status weewx`

Now everything should be working. Data should arrive and be displayed on the website.
	