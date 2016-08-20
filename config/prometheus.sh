#!/bin/bash

# Replace all ENVARS in all config files
find /etc/config -type f -exec sed -i -e s/SMTP_ACCOUNT/${SMTP_ACCOUNT}/g \
-e s/SMTP_PASSWORD/${SMTP_PASSWORD}/g \
-e s/SMTP_HOST/${SMTP_HOST}/g \
-e s/THRESHOLD_CPU/${THRESHOLD_CPU}/g \
-e s/THRESHOLD_MEM/${THRESHOLD_MEM}/g \
-e s/THRESHOLD_FS/${THRESHOLD_FS}/g \
-e s/RESIN_APP_ID/${RESIN_APP_ID}/g \
-e s/RESIN_DEVICE_UUID/${RESIN_DEVICE_UUID}/g \
-e s/ALERTMANAGER_PATH/alertmanager-${ALERTMANAGER_VERSION}.${DIST_ARCH}/g \
{} \;

# mv config files to correct dir
mv -t /etc/prometheus-$PROMETHEUS_VERSION.$DIST_ARCH/ /etc/config/prometheus.yml /etc/config/alert.rules
mv -t /etc/alertmanager-$ALERTMANAGER_VERSION.$DIST_ARCH/ /etc/config/alertmanager.yml /etc/config/default.tmpl

# Start the node exporter
cd /etc/node_exporter-$NODE_EXPORTER_VERSION.$DIST_ARCH \
  && ./node_exporter &
# Start prometheus server
mkdir -p /data/prometheus
cd /etc/prometheus-$PROMETHEUS_VERSION.$DIST_ARCH \
  && ./prometheus -web.listen-address ":80" \
  -storage.local.path "/data/prometheus" -storage.local.retention ${STORAGE_LOCAL_RETENTION} \
  -alertmanager.url "http://localhost:9093" &
# Load configs from envars && start alertmanager
cd /etc/alertmanager-$ALERTMANAGER_VERSION.$DIST_ARCH \
  && ./alertmanager -config.file=alertmanager.yml &
