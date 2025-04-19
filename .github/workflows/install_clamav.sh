set -eu
## For Debian Container running as root

apt-get update
apt-get install -y --no-install-recommends clamav clamav-daemon

freshclam

clamscan --version

cat /etc/clamav/clamd.conf

cp /etc/clamav/clamd.conf /etc/clamav/clamd.conf.sample
sed -e "s|.*\(LocalSocket\) .*|\1 /tmp/clamd.sock|" \
-e "s|.*\(User\) .*|\1 root|" \
"/etc/clamav/clamd.conf.sample" > "/etc/clamav/clamd.conf"