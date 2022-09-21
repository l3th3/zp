#!/bin/bash

export PROJECT_DIR=$(pwd)
export SD_ZAP_DIR="${PROJECT_DIR}/zap"
export SOURCE_IFACE_ADDR="http://127.0.0.1:8080"
export JOURNALIST_IFACE_ADDR="http://127.0.0.1:8081"

# source "$SD_ZAP_DIR/scripts/lib.sh"

function zap_scan() {
    context="$1"
    addr="$2"
    outfile="$3"
    contextfile="$SD_ZAP_DIR/contexts/${context}.context"
    
    echo "contextfile: ${contextfile}"
    echo "addr: ${addr}"
    echo "outfile: ${outfile}"

    echo "zap-cli open-url '$addr'"
    zap-cli open-url "$addr"
    echo "zap-cli context import '$contextfile'"
    zap-cli context import "$contextfile"
    echo "zap-cli active-scan ;$addr'"
    zap-cli active-scan --context-name "$context" "$addr"
    echo "zap-cli report -f xml -o '$outfile'"
    zap-cli report -f xml -o "$outfile"
}

function test_port_connection() {
port=$1
for i in $(seq 15)
do
    if [ $(nc -z 127.0.0.1 $port; echo $?) -eq 0 ]
    then
        echo "Connection to port $port successful"
        break
    fi
    if [ $i -ge 60 ]
    then
        echo "Failed to establish a connection to port $port"
    fi
    sleep 5
done
}

# zap_installation

# start_zaproxy_daemon

# make dev-detatched &
# export SDPID=$!

echo "Testing zap proxy port connection..."
test_port_connection 8090
echo "Testing source interface connection..."
test_port_connection 8080
echo "Testing journalist interface connection..."
test_port_connection 8081

zap_scan source_noauth "$SOURCE_IFACE_ADDR" "~/project/zap_source_iface.xml"
zap_scan source_auth "$SOURCE_IFACE_ADDR" "~/project/zap_source_iface.xml"
zap_scan journalist_noauth "$JOURNALIST_IFACE_ADDR" "~/project/zap_journalist_iface.xml"
zap_scan journalist_auth "$JOURNALIST_IFACE_ADDR" "~/project/zap_journalist_iface.xml"

# kill -9 $SDPID

# stop_zaproxy_daemon