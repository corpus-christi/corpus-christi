# Utility Makefile to configure CC server

NGINX_DIR=/etc/nginx/sites-available
SUPER_DIR=/etc/supervisor/conf.d
CONF_NAME=corpus-christi.conf

all: conf-all

conf-nginx:
	$(CP) ./cc-nginx.conf $NGINX_DIR/$CONF_NAME

conf-super:
	$(CP) ./cc-super.conf $SUPER_DIR/$CONF_NAME

conf-all: conf-nginx conf-super
