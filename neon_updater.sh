date > /home/neon/logs/updater.log;
echo "Current version: " >> /home/neon/logs/updater.log;
(neon --version | grep 'Neon version .*') > /home/neon/version;
cat /home/neon/version >> /home/neon/logs/updater.log;
echo "Starting updater service..." >> /home/neon/logs/updater.log;
sudo systemctl start neon-updater >> /home/neon/logs/updater.log;
sudo systemctl status neon-updater >> /home/neon/logs/updater.log;
echo "New current version: " >> /home/neon/logs/updater.log;
(neon --version | grep 'Neon version .*') > /home/neon/version;
cat /home/neon/version >> /home/neon/logs/updater.log;
echo "End of updater script" >> /home/neon/logs/updater.log;
