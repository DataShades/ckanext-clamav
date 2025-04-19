set -eu
## For Debian Container running

while [ ! -S "/tmp/clamd.sock" ]; do
			if [ "${_timeout:=0}" -gt "${CLAMD_STARTUP_TIMEOUT:=1800}" ]; then
				echo
				echo "Failed to start clamd"
				exit 1
			fi
			printf "\r%s" "Socket for clamd not found yet, retrying (${_timeout}/${CLAMD_STARTUP_TIMEOUT}) ..."
			sleep 1
			_timeout="$((_timeout + 1))"
		done
		echo "socket found, clamd started."