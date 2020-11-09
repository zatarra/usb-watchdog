ifeq ($(PREFIX),)
    PREFIX := /usr/local
endif


all:
	pip3 install -r requirements.txt

install:
	install -d $(PREFIX)/sbin
	install -m 775 watchdog.py $(PREFIX)/sbin/
	install -m 664 usb-watchdog.service /etc/systemd/system
	systemctl daemon-reload
	install -m 664 99-usbwatchdog.rules /etc/udev/rules.d
	udevadm control --reload-rules && udevadm trigger

enable:
	systemctl enable --now usb-watchdog.service
	
restart:
	systemctl restart usb-watchdog.service
	
status:
	systemctl status usb-watchdog.service