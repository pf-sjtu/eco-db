��ʼ����
	python3-dev
	MySQL��host='localhost', port = 3306, user='root', passwd='mmtt2356', db = mysql
	Python3: numpy, pandas, mysqlclient, datetime, xlrd, xlwt
	MySQL: ����·���޸�
		mysql --help | grep 'my.cnf'
		[mysqld] ��
			secure_file_priv=
			local-infile=1
		[mysql] ��
			local-infile=1
		service mysql start/ stop/ restart

		ע�����⣺
		1. �û�localhost��%������
		CREATE USER 'webUser' @'%' IDENTIFIED WITH mysql_native_password BY '516150910019';
		GRANT SELECT, CREATE TEMPORARY TABLES ON station_db.* TO 'webUser' @'%';
		2. /r/n������
		3. load data local infile������

		�����������https://blog.csdn.net/netyeaxi/article/details/94588733
		https://www.cnblogs.com/conanwang/p/6118731.html

screen
python3-dev/ python3-devel (���ܻ���Ҫpython-dev/ python-devel)
pip3 install numpy pandas mysqlclient datetime xlrd xlwt
MySQL: ����·���޸�
mysql --help | grep 'my.cnf'
[mysqld] ��
	secure_file_priv=
	local-infile=1
[mysql] ��
	local-infile=1
service mysql start/ stop/ restart
service mysqld start/ stop/ restart


�û�Ȩ�ޣ�
5.4:
CREATE USER 'webUser' @'localhost' IDENTIFIED WITH mysql_native_password BY '516150910019';

5.6+:
CREATE USER 'webUser' @'localhost' IDENTIFIED BY '516150910019';

GRANT SELECT ON station_db.* TO 'webUser' @'localhost';
FLUSH PRIVILEGES;

USE station_db;
LOAD DATA INFILE "/www/wwwroot/ftp/web/db20200410/cm.csv" IGNORE INTO TABLE cm FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';
LOAD DATA INFILE "ftp/web/db20200410/jh.csv" INTO TABLE jh FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';
LOAD DATA INFILE "ftp/web/db20200410/zsgy.csv" INTO TABLE zsgy FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';